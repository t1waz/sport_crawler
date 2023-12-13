import time
from typing import List

import dramatiq
from sqlalchemy.orm import sessionmaker

from common.tables import ProviderTable, GymTable
from scraper.db import engine
from scraper.jobs.get_energy_fitness_class import get_energy_fitness_class

PROVIDER_NAME = "energy_fitness"

Session = sessionmaker(bind=engine)


def get_gyms() -> List[GymTable]:
    with Session() as session:
        energy_fitness_provider = (
            session.query(ProviderTable)
            .filter(ProviderTable.name == PROVIDER_NAME)
            .first()
        )
        if not energy_fitness_provider:
            print("no zdrofit provider")  # TODO move to logger
            return []

        return session.query(GymTable).filter(
            GymTable.provider_id == energy_fitness_provider.id
        )


@dramatiq.actor
def get_energy_fitness_classes():
    print("start get_zdrofit_classes")  # TODO move to logger

    zdrofit_gyms = get_gyms()
    for gym in zdrofit_gyms:
        get_energy_fitness_class.send(gym.id, gym.name, gym.url)
        time.sleep(0.5)
