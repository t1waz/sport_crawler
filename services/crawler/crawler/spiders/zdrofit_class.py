import uuid
from typing import List, Optional

import scrapy
from bs4 import BeautifulSoup
from bs4.element import Tag

from common.entites import SportClassData


class ZdrofitClassSpider(scrapy.Spider):
    """
    Read all Zdrofit for given url.
    """

    name = "zdrofit_class"

    def __init__(self, *args, **kwargs) -> None:
        self._days: List[str] = []
        self._hours: List[str] = []
        self.job_id = kwargs.get("_job")  # TODO move to mixin
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
        rows = self._table.find_all("tr")[1:]

        self._hours = [row.find("th").text for row in rows]

    def _read_days(self) -> None:
        rows = list(self._table.find("thead").find("tr"))[1:8]

        self._days = [row.find("strong").text for row in rows]

    def _read_sport_records(self, table_data: Tag):
        for i, d in enumerate(table_data.find_all("td")[: len(self._days)]):
            d = d.find("div", {"class": "club-schedule-item"})
            if not d:
                continue
            start_hour, end_hour = d.find_all("strong")[1].text.strip().split(" - ")
            self._sports.append(
                SportClassData(
                    id=str(uuid.uuid4()),
                    end_hour=end_hour,
                    name=d.find("a").text,
                    start_hour=start_hour,
                    day=f"{self._days[i]} 2023",
                )
            )

    def _read_sports(self) -> None:
        self._sports = []
        table_body = self._table.find("tbody")
        for data in table_body.find_all("tr")[: len(self._hours)]:
            self._read_sport_records(table_data=data)

    def parse(self, response, **kwargs) -> dict:
        table_html = response.selector.xpath("/html/body/main/section/table").get()
        self._table = BeautifulSoup(table_html, features="lxml")

        self._read_hours()
        self._read_days()
        self._read_sports()

        return {"classes": self.sports}

    @property
    def sports(self) -> List[SportClassData]:
        if self._sports is None:
            raise ValueError("read first")

        return self._sports
