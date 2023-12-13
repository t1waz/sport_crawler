import uuid
from dataclasses import asdict
from typing import Optional, List, Any

import dramatiq
from bs4 import BeautifulSoup
from bs4.element import Tag
from sqlalchemy.orm import sessionmaker

from common.entites import SportGymData
from common.tables import ProviderTable, GymTable
from scraper import settings  # type: ignore
from scraper.db import engine
from scraper.logic import ScraperJobLogic

Session = sessionmaker(bind=engine)


PROVIDER_NAME = "energy_fitness"


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


class GetEnergyFitnessGymsJob(ScraperJobLogic):
    JOB_NAME = "get energy fitness gyms"

    def __init__(self, *args, **kwargs) -> None:
        self._gyms: List[SportGymData] = []
        super().__init__(*args, **kwargs)

    def _read_row(self, row: Tag) -> None:
        data_placeholder = row.find("a")
        if not data_placeholder:
            return

        gym_name = data_placeholder.text.lower()
        if gym_name not in self.gym_names:
            self._gyms.append(
                SportGymData(
                    address="",
                    name=gym_name,
                    id=str(uuid.uuid4()),
                    provider=PROVIDER_NAME,
                    url=data_placeholder["href"],
                )
            )

    def _read_section(self, section: Tag) -> None:
        for row in section.find_all("td"):
            self._read_row(row=row)

    def process_data(self, page_data: str) -> Optional[Any]:
        page = BeautifulSoup(page_data, features="lxml")
        table = page.find("table", {"class": "grafikTable"})
        table_body = table.find("tbody")

        for section in table_body.find_all("tr"):
            self._read_section(section=section)

        return self.gyms

    @property
    def gyms(self) -> List[SportGymData]:
        return self._gyms

    @property
    def gym_names(self) -> List[str]:
        return [g.name for g in self.gyms]

    @property
    def url(self) -> str:
        return "https://www.energyfitness.pl/grafik-zajec-1.php"


@dramatiq.actor
def get_energy_fitness_gyms():
    data = GetEnergyFitnessGymsJob().run()
    if data:
        save_sport_gym_data(data=data)
