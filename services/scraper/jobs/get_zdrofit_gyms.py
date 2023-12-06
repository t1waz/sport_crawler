import uuid
from dataclasses import asdict
from typing import Optional, List, Any

import dramatiq
from bs4 import BeautifulSoup
from bs4.element import Tag
from sqlalchemy.orm import Session

from common.entites import SportGymData
from common.tables import ProviderTable, GymTable
from scraper import settings  # type: ignore
from scraper.db import engine
from scraper.logic import ScraperJobLogic


DOMAIN = "zdrofit.pl"


def save_sport_gym_data(data: List[SportGymData]) -> None:
    with Session(engine) as session:
        zdrofit_provider = (
            session.query(ProviderTable).filter_by(name="zdrofit").first()
        )
        if not zdrofit_provider:
            zdrofit_provider = ProviderTable(id=str(uuid.uuid4()), name="zdrofit")
            session.add(zdrofit_provider)

        existing_gym_names = session.query(GymTable.name).filter(
            GymTable.provider == zdrofit_provider
        ) or []

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


class GetZdrofitGymsJob(ScraperJobLogic):
    JOB_NAME = "get zdrofit gyms"

    def __init__(self, *args, **kwargs) -> None:
        self._gyms = []
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_section_address(section: Tag) -> str:
        return section.find("p").text

    @staticmethod
    def _get_section_name(section: Tag) -> str:
        return f'Zdrofit {section.find("a").text}'

    @staticmethod
    def _get_section_url(section: Tag) -> str:
        return f'https://{DOMAIN}{section.find("a")["href"].replace("//", "/")}'

    def _parse_section(self, section: Tag) -> None:
        for s in section.find("ul"):
            self._gyms.append(
                SportGymData(
                    provider="zdrofit",
                    id=str(uuid.uuid4()),
                    url=self._get_section_url(section=s),
                    name=self._get_section_name(section=s),
                    address=self._get_section_address(section=s),
                )
            )

    def process_data(self, page_data: str) -> Optional[Any]:
        page = BeautifulSoup(page_data, features="lxml")
        table = page.find(id="lista")

        for section in table.find_all("section"):
            self._parse_section(section=section)

        return self.gyms

    @property
    def url(self) -> str:
        return "https://zdrofit.pl/grafik-zajec"

    @property
    def gyms(self) -> List[SportGymData]:
        return self._gyms


@dramatiq.actor
def get_zdrofit_gyms():
    data = GetZdrofitGymsJob().run()
    save_sport_gym_data(data=data)
