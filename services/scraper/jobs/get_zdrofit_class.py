import datetime
import dramatiq
import uuid
from bs4 import BeautifulSoup
from bs4.element import Tag
from sqlalchemy.orm import sessionmaker
from typing import List, Optional, Any

from common.entites import SportClassData
from common.tables import GymClass, GymClassBook, GymTable
from scraper import settings  # type: ignore
from scraper.db import engine
from scraper.logic import ScraperJobLogic

Session = sessionmaker(bind=engine)

MONTH_MAPPER = {
    "styczeń": 1,
    "stycznia": 1,
    "styczen": 1,
    "luty": 2,
    "marzec": 3,
    "marca": 3,
    "kwiecień": 4,
    "kwietnia": 4,
    "kwiecien": 4,
    "maj": 5,
    "maja": 5,
    "czerwiec": 6,
    "czerwca": 6,
    "lipiec": 7,
    "lipca": 7,
    "sierpień": 8,
    "sierpien": 8,
    "sierpnia": 8,
    "wrzesień": 9,
    "wrzesien": 9,
    "września": 9,
    "wrzesnia": 9,
    "październik": 10,
    "października": 10,
    "pazdziernik": 10,
    "listopad": 11,
    "listopada": 11,
    "grudzień": 12,
    "grudzien": 12,
    "grudnia": 12,
}


def get_datetime(entity: SportClassData, hour_str: str) -> datetime.datetime:
    day, month, year = entity.day.lower().split(" ")
    hour, minute = hour_str.lower().split(":")

    return datetime.datetime(
        day=int(day),
        year=int(year),
        hour=int(hour),
        minute=int(minute),
        month=MONTH_MAPPER[month],
    )


def _save_gym_class(gym, session, class_data: SportClassData) -> None:
    gym_class = (
        session.query(GymClass)
        .filter(GymClass.gym_id == gym.id, GymClass.name == class_data.name)
        .first()
    )
    if not gym_class:
        gym_class = GymClass(id=str(uuid.uuid4()), name=class_data.name, gym_id=gym.id)
        session.add(gym_class)

    class_book_start_at = get_datetime(
        entity=class_data, hour_str=class_data.start_hour
    )
    class_book_finish_at = get_datetime(entity=class_data, hour_str=class_data.end_hour)

    class_book = (
        session.query(GymClassBook)
        .filter(
            GymClassBook.gym_class_id == gym_class.id,
            GymClassBook.start_at >= class_book_start_at,
            GymClassBook.end_at <= class_book_finish_at,
        )
        .first()
    )
    if class_book:
        class_book.is_active = False
    else:
        class_book = GymClassBook(
            is_active=True,
            id=str(uuid.uuid4()),
            gym_class_id=gym_class.id,
            end_at=class_book_finish_at,
            start_at=class_book_start_at,
        )
    session.add(class_book)


def save_zdrofit_gym_classes(data: List[SportClassData], gym_id) -> None:
    with Session() as session:
        gym = session.query(GymTable).filter(GymTable.id == gym_id).first()
        if not gym:
            raise ValueError("cannot save, no gym_id")

        for gym_class in data:
            _save_gym_class(gym=gym, session=session, class_data=gym_class)

        session.commit()


class GetZdrofitGymClassJob(ScraperJobLogic):
    JOB_NAME = "get zdrofit gym class"

    def __init__(self, gym_class_url: str, *args, **kwargs) -> None:
        self._classes = []
        self._table = None
        self._url = gym_class_url
        self._days: List[str] = []
        self._hours: List[str] = []

        super().__init__(*args, **kwargs)

    def _read_hours(self) -> None:
        rows = self._table.find_all("tr")[1:]

        self._hours = [row.find("th").text for row in rows]

    def _read_days(self) -> None:
        rows = list(self._table.find("thead").find("tr"))[1:8]

        self._days = [row.find("strong").text for row in rows]

    def _read_sport_records(self, table_data: Tag):
        for i, d in enumerate(table_data.find_all("td")[: len(self._days)]):
            d = d.find("div", {"class": "club-schedule-item"})
            if not d:
                continue
            start_hour, end_hour = d.find_all("strong")[1].text.strip().split(" - ")
            self._classes.append(
                SportClassData(
                    id=str(uuid.uuid4()),
                    end_hour=end_hour,
                    name=d.find("a").text,
                    start_hour=start_hour,
                    day=f"{self._days[i]} {datetime.datetime.now().year}",
                )
            )

    def _read_sports(self) -> None:
        table_body = self._table.find("tbody")
        for data in table_body.find_all("tr")[: len(self._hours)]:
            self._read_sport_records(table_data=data)

    def process_data(self, page_data: str) -> Optional[Any]:
        page = BeautifulSoup(page_data, features="lxml")
        self._table = page.find("table", {"class": "schedule"})

        self._read_hours()
        self._read_days()
        self._read_sports()

        return self.classes

    @property
    def url(self) -> str:
        return self._url

    @property
    def classes(self) -> List[SportClassData]:
        return self._classes


@dramatiq.actor
def get_zdrofit_class(gym_id: str, gym_name: str, gym_url: str) -> None:
    print(f"start get_zdrofit_class for gym: {gym_name}")  # TODO logger
    data = GetZdrofitGymClassJob(gym_class_url=gym_url).run()
    if data:
        save_zdrofit_gym_classes(data=data, gym_id=gym_id)
