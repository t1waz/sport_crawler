import uuid
from dataclasses import asdict
from typing import Any

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from sqlalchemy.orm import Session

from common.tables import ProviderTable, GymTable
from scraper.db import engine
from scraper.logic import ScraperJobLogic


class GetZdrofitGymsLogic(ScraperJobLogic):
    SPIDER_NAME = "zdrofit_gym"

    def get_spider_kwargs(self) -> dict:
        return {"start_url": "https://zdrofit.pl/grafik-zajec"}

    def process_data(self, data: Any) -> None:
        data = data["gyms"]

        with Session(engine) as session:
            zdrofit_provider = (
                session.query(ProviderTable).filter_by(name="zdrofit").first()
            )
            if not zdrofit_provider:
                zdrofit_provider = ProviderTable(id=str(uuid.uuid4()), name="zdrofit")
                session.add(zdrofit_provider)

                existing_gym_names = session.query(GymTable.name).filter(
                    GymTable.provider == zdrofit_provider
                )
                new_gyms = [d for d in data if d.name not in existing_gym_names]
                session.add_all(
                    [
                        GymTable(
                            is_active=True,
                            provider_id=zdrofit_provider.id,
                            **{k: v for k, v in asdict(d).items() if k != "provider"},
                        )
                        for d in new_gyms
                    ]
                )
                not_active_gyms = (
                    session.query(GymTable)
                    .populate_existing()
                    .with_for_update()
                    .filter(GymTable.name.not_in([d.name for d in new_gyms]))
                )
                for not_active_gym in not_active_gyms:
                    not_active_gym.is_active = False

                session.add_all(not_active_gyms)

            session.commit()


@dramatiq.actor
def get_zdrofit_gyms():
    print("start get_zdrofit_gyms")  # TODO move to logger
    GetZdrofitGymsLogic().run()
