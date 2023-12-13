import datetime
import uuid
from typing import List, Optional, Any, Tuple

import dramatiq
from bs4 import BeautifulSoup
from bs4.element import Tag
from sqlalchemy.orm import sessionmaker

from common.entites import SportClassData
from common.tables import GymClass, GymClassBook, GymTable
from scraper import settings  # type: ignore
from scraper.db import engine
from scraper.logic import ScraperJobLogic

Session = sessionmaker(bind=engine)

DAY_MAPPER = {
    "poniedziałek": 0,
    "poniedzialek": 0,
    "wtorek": 1,
    "środa": 2,
    "sroda": 2,
    "czwartek": 3,
    "piątek": 4,
    "piatek": 4,
    "sobota": 5,
    "niedziela": 6,
}


def get_class_start_and_end_datetimes(
    entity: SportClassData,
) -> Tuple[datetime.datetime, datetime.datetime]:
    now = datetime.datetime.now()
    text_day, year = entity.day.split(" ")
    text_day = text_day.lower()
    start_hour, start_minute = entity.start_hour.lower().split(":")
    end_timedelta = int(entity.end_hour.strip("min").strip(" ").split("+")[1])

    start_datetime = datetime.datetime(
        year=now.year,
        month=now.month,
        day=now.day + (DAY_MAPPER[text_day] - now.weekday()),
        hour=int(start_hour),
        minute=int(start_minute),
    )
    end_datetime = start_datetime + datetime.timedelta(minutes=end_timedelta)

    return start_datetime, end_datetime


def _save_gym_class(gym, session, class_data: SportClassData) -> None:
    gym_class = (
        session.query(GymClass)
        .filter(GymClass.gym_id == gym.id, GymClass.name == class_data.name)
        .first()
    )
    if not gym_class:
        gym_class = GymClass(id=str(uuid.uuid4()), name=class_data.name, gym_id=gym.id)
        session.add(gym_class)

    class_book_start_at, class_book_finish_at = get_class_start_and_end_datetimes(
        entity=class_data
    )

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


def save_energy_fitness_gym_classes(data: List[SportClassData], gym_id) -> None:
    with Session() as session:
        gym = session.query(GymTable).filter(GymTable.id == gym_id).first()
        if not gym:
            raise ValueError("cannot save, no gym_id")

        for gym_class in data:
            _save_gym_class(gym=gym, session=session, class_data=gym_class)

        session.commit()


class GetEnergyFitnessGymClassJob(ScraperJobLogic):
    JOB_NAME = "get energy fitness gym class"

    def __init__(self, gym_class_url: str, *args, **kwargs) -> None:
        self._url = gym_class_url
        self._days: List[str] = []
        self._hours: List[str] = []
        self._classes: List[SportClassData] = []
        self._table: Optional[BeautifulSoup] = None

        super().__init__(*args, **kwargs)

    def _read_hours(self) -> None:
        rows = self._table.find("tbody").find_all("tr")
        for row in rows:
            hour_data = row.find("td", {"class": "hour"})
            if not hour_data:
                continue

            self._hours.append(hour_data.text.strip())

    def _read_days(self) -> None:
        rows = list(self._table.find("thead").find("tr").find_all("td"))[1:8]

        self._days = [row.find("a").text for row in rows]

    def _read_sport_records(self, table_data: Tag, hour: str) -> None:
        for i, d in enumerate(table_data.find_all("td")[1 : len(self._days) + 1]):
            d = d.find("div", {"class": "event"})
            if not d:
                continue

            start_hour = hour
            end_hour = f'{start_hour}+{d.find("span", {"class": "eventlength"}).text.strip()}'  # TODO parse it

            self._classes.append(
                SportClassData(
                    id=str(uuid.uuid4()),
                    end_hour=end_hour,
                    start_hour=start_hour,
                    day=f"{self._days[i]} 2023",
                    name=d.find("p", {"class": "event_name"}).text,
                )
            )

    def _read_classes(self) -> None:
        self._sports = []
        table_body = self._table.find("tbody")
        for i, data in enumerate(table_body.find_all("tr")[: len(self._hours)]):
            self._read_sport_records(table_data=data, hour=self._hours[i])

    def process_data(self, page_data: str) -> Optional[Any]:
        page = BeautifulSoup(page_data, features="lxml")
        self._table = page.find("table", {"class": "calendar_table week"})

        self._read_hours()
        self._read_days()
        self._read_classes()

        return self._classes

    @property
    def url(self) -> str:
        return self._url

    @property
    def classes(self) -> List[SportClassData]:
        return self._classes


@dramatiq.actor
def get_energy_fitness_class(gym_id: str, gym_name: str, gym_url: str) -> None:
    print(f"start get_energy_fitness_class for gym: {gym_name}")  # TODO logger
    data = GetEnergyFitnessGymClassJob(gym_class_url=gym_url).run()
    if data:
        save_energy_fitness_gym_classes(data=data, gym_id=gym_id)
