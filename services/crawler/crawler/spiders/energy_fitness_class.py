import uuid
from typing import List, Optional

import scrapy
from bs4 import BeautifulSoup
from bs4.element import Tag

from common.entites import SportClassData


class EnergyFitnessClassSpider(scrapy.Spider):
    """
    Read all Energy Fitness classes for given url.
    """

    name = "energy_fitness_class"

    def __init__(self, *args, **kwargs) -> None:
        self._days: List[str] = []
        self._hours: List[str] = []
        self.url = kwargs.get("start_url")
        self._sports: Optional[List[SportClassData]] = None
        self._table: Optional[BeautifulSoup] = None

        super().__init__(*args, **kwargs)

    def start_requests(self) -> scrapy.Request:
        yield scrapy.Request(
            url=self.url,
            meta={"playwright": True},
        )

    def _read_hours(self) -> None:
        rows = self._table.find("tbody").find_all("tr")
        for row in rows:
            hour_data = row.find("td", {"class": "hour"})
            if not hour_data:
                continue

            self._hours.append(hour_data.text.strip())

    def _read_days(self) -> None:
        rows = list(self._table.find("thead").find("tr").find_all("td"))[1:8]

        self._days = [row.find("a").text for row in rows]

    def _read_sport_records(self, table_data: Tag, hour: str) -> None:
        for i, d in enumerate(table_data.find_all("td")[1 : len(self._days) + 1]):
            d = d.find("div", {"class": "event"})
            if not d:
                continue

            start_hour = hour
            end_hour = f'{start_hour}+{d.find("span", {"class": "eventlength"}).text.strip()}'  # TODO parse it

            self._sports.append(
                SportClassData(
                    id=str(uuid.uuid4()),
                    end_hour=end_hour,
                    start_hour=start_hour,
                    day=f"{self._days[i]} 2023",
                    name=d.find("p", {"class": "event_name"}).text,
                )
            )

    def _read_sports(self) -> None:
        self._sports = []
        table_body = self._table.find("tbody")
        for i, data in enumerate(table_body.find_all("tr")[: len(self._hours)]):
            self._read_sport_records(table_data=data, hour=self._hours[i])

    def parse(self, response, **kwargs) -> dict:
        table_html = response.selector.xpath(
            "/html/body/div[1]/div/div/div[2]/div[1]/div[1]/table"
        ).get()
        self._table = BeautifulSoup(table_html, features="lxml")

        self._read_hours()
        self._read_days()
        self._read_sports()

        return {"sports": self.sports}

    @property
    def sports(self) -> List[SportClassData]:
        if self._sports is None:
            raise ValueError("read first")

        return self._sports
