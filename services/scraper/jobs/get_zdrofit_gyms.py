import dramatiq
import uuid
from bs4 import BeautifulSoup
from bs4.element import Tag
from dataclasses import asdict
from sqlalchemy.orm import sessionmaker
from typing import Optional, List, Any

from common.entites import SportGymData
from common.tables import ProviderTable, GymTable
from scraper import settings  # type: ignore
from scraper.db import engine
from scraper.logic import ScraperJobLogic

DOMAIN = "zdrofit.pl"
PROVIDER_NAME = "zdrofit"

Session = sessionmaker(bind=engine)


def save_sport_gym_data(data: List[SportGymData]) -> None:
    with Session() as session:
        provider = session.query(ProviderTable).filter_by(name=PROVIDER_NAME).first()
        if not provider:
            provider = ProviderTable(id=str(uuid.uuid4()), name=PROVIDER_NAME)
            session.add(provider)

        existing_gym_names = next(
            iter(
                zip(*session.query(GymTable.name).filter(GymTable.provider == provider))
            ),
            [],
        )

        new_gyms = [d for d in data if d.name not in existing_gym_names]
        session.add_all(
            [
                GymTable(
                    is_active=True,
                    provider_id=provider.id,
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
                    id=str(uuid.uuid4()),
                    provider=PROVIDER_NAME,
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
    if data:
        save_sport_gym_data(data=data)
