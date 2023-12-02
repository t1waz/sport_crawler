import asyncio
import uuid
from dataclasses import asdict
from typing import Any

import dramatiq
from bs4 import BeautifulSoup
from bs4.element import Tag
from playwright.async_api import async_playwright, Playwright
from sqlalchemy.orm import Session

from common import constants
from common.entites import SportGymData
from common.tables import ProviderTable, GymTable
from scraper import settings
from scraper.db import engine
from scraper.services import ScrapJobService


DOMAIN = "zdrofit.pl"
URL = "https://zdrofit.pl/grafik-zajec"


def _get_section_address(section: Tag) -> str:
    return section.find("p").text


def _get_section_name(section: Tag) -> str:
    return f'Zdrofit {section.find("a").text}'


def _get_section_url(section: Tag) -> str:
    return f'https://{DOMAIN}{section.find("a")["href"].replace("//", "/")}'


async def get_page_data(playwright: Playwright):
    chromium = playwright.chromium
    browser = await chromium.launch(
        headless=True,
        proxy={
            "server": settings.PROXY_SERVER,
            "username": settings.USERNAME,
            "password": settings.PASSWORD,
        }
    )
    page = await browser.new_page()
    await page.goto(URL)

    table_data = page.locator('xpath=//*[@id="lista"]')
    table = BeautifulSoup(await table_data.inner_html(), features="lxml")

    await browser.close()

    gyms = []
    for section in table.find_all("section"):
        for s in section.find("ul"):
            gyms.append(
                SportGymData(
                    provider="zdrofit",
                    id=str(uuid.uuid4()),
                    url=_get_section_url(section=s),
                    name=_get_section_name(section=s),
                    address=_get_section_address(section=s),
                )
            )

    return gyms


def process_data(data: Any) -> None:
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


async def main():
    job_service = ScrapJobService.create_new(spider_name="get_zdrofit_gyms")

    async with async_playwright() as playwright:
        data = await get_page_data(playwright=playwright)
    job_service.update_status(status=constants.ScrapJobStatus.RUNNING)

    process_data(data=data)

    job_service.update_status(status=constants.ScrapJobStatus.FINISH, is_finished=True)
    print("get zdrofit gyms success !")  # TODO logger


@dramatiq.actor
def get_zdrofit_gyms():
    asyncio.run(main())
