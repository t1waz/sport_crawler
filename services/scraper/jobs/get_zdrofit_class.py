import datetime
import uuid
from typing import Any

import dramatiq
from sqlalchemy.orm import Session

from common.entites import SportClassData
from common.tables import GymClass, GymTable, GymClassBook
from scraper.db import engine
from scraper.logic import ScraperJobLogic


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


class GetZdrofitClassLogic(ScraperJobLogic):
    SPIDER_NAME = "zdrofit_class"

    def __init__(self, gym: GymTable, *args, **kwargs) -> None:
        self._gym = gym
        super().__init__(*args, **kwargs)

    def get_spider_kwargs(self) -> dict:
        return {"start_url": self._gym.url}

    def _process_gym_class(self, session, class_data: SportClassData) -> None:
        gym_class = (
            session.query(GymClass)
            .filter(GymClass.gym_id == self._gym.id, GymClass.name == class_data.name)
            .first()
        )
        if not gym_class:
            gym_class = GymClass(
                id=str(uuid.uuid4()), name=class_data.name, gym_id=self._gym.id
            )
            session.add(gym_class)

        class_book_start_at = get_datetime(
            entity=class_data, hour_str=class_data.start_hour
        )
        class_book_finish_at = get_datetime(
            entity=class_data, hour_str=class_data.end_hour
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

    def process_data(self, data: Any) -> None:
        with Session(engine) as session:
            for gym_class in data["classes"]:
                self._process_gym_class(session=session, class_data=gym_class)

            session.commit()


@dramatiq.actor
def get_zdrofit_class(gym_id: str) -> None:
    print("start get_zdrofit_class for gym ", gym_id)  # TODO move to logger
    with Session(engine) as session:
        gym = session.query(GymTable).filter(GymTable.id == gym_id).first()

    if gym is None:
        return

    GetZdrofitClassLogic(gym=gym).run()
