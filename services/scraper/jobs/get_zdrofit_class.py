import uuid
from typing import Any

import dramatiq
from sqlalchemy.orm import Session

from common.entites import SportClassData
from common.tables import GymClass, GymTable
from scraper.db import engine
from scraper.logic import ScraperJobLogic


class GetZdrofitClassLogic(ScraperJobLogic):
    SPIDER_NAME = "zdrofit_class"

    def __init__(self, gym: GymTable, *args, **kwargs) -> None:
        self._gym = gym
        super().__init__(*args, **kwargs)

    def get_spider_kwargs(self) -> dict:
        return {"start_url": self._gym.url}

    def _process_gym_class(self, session, class_data: SportClassData) -> None:
        gym_class = session.query(GymClass).filter(GymClass.gym_id == self._gym.id, GymClass.name == class_data.name)
        if not gym_class:
            gym_class = GymClass(id=str(uuid.uuid4()), name=class_data.name, gym_id=self._gym.id)
            session.add(gym_class)

    def process_data(self, data: Any) -> None:
        with Session(engine) as session:
            for gym_class in data["classes"]:
                self._process_gym_class(session=session, class_data=gym_class)

            session.commit()
            print("added class ", gym_class)


@dramatiq.actor
def get_zdrofit_class(gym_id: str) -> None:
    with Session(engine) as session:
        gym = session.query(GymTable).filter(GymTable.id == gym_id).first()

    if gym is None:
        return

    GetZdrofitClassLogic(gym=gym).run()
