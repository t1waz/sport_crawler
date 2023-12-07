import dramatiq
import random
import time
from sqlalchemy.orm import sessionmaker
from typing import List

from common.tables import ProviderTable, GymTable
from scraper.db import engine
from scraper.jobs.get_zdrofit_class import get_zdrofit_class

Session = sessionmaker(bind=engine)


def get_gyms() -> List[GymTable]:
    with Session() as session:
        zdrofit_provider = (
            session.query(ProviderTable).filter(ProviderTable.name == "zdrofit").first()
        )
        if not zdrofit_provider:
            print("no zdrofit provider")  # TODO move to logger
            return []

        return session.query(GymTable).filter(
            GymTable.provider_id == zdrofit_provider.id
        )


@dramatiq.actor
def get_zdrofit_classes():
    print("start get_zdrofit_classes")  # TODO move to logger

    zdrofit_gyms = get_gyms()
    for gym in zdrofit_gyms:
        get_zdrofit_class.send(gym.id, gym.name, gym.url)
        time.sleep(random.randint(1, 3))
