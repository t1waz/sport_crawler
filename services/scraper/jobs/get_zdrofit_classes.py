import dramatiq
from sqlalchemy.orm import Session

from common.tables import ProviderTable, GymTable
from scraper.db import engine
from scraper.jobs.get_zdrofit_class import get_zdrofit_class


@dramatiq.actor
def get_zdrofit_classes():
    print("start get_zdrofit_classes")  # TODO move to logger

    with Session(engine) as session:
        zdrofit_provider = (
            session.query(ProviderTable).filter(ProviderTable.name == "zdrofit").first()
        )
        if not zdrofit_provider:
            print("no zdrofit provider")  # TODO move to logger
            return

        zdrofit_gyms = session.query(GymTable).filter(
            GymTable.provider_id == zdrofit_provider.id
        )
        for gym in zdrofit_gyms:
            get_zdrofit_class.send(gym.id)
