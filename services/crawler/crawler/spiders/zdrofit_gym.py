from typing import List, Optional

import scrapy
from bs4 import BeautifulSoup
from bs4.element import Tag

from common.entites import SportGymData
import uuid
from urllib.parse import urlparse


class ZdrofitGymSpider(scrapy.Spider):
    """
    Read all Zdrofit gyms (places).
    """

    name = "zdrofit_gym"

    def __init__(self, start_url: str, *args, **kwargs) -> None:
        self.url = start_url
        self._domain = urlparse(self.url).netloc
        self.job_id = kwargs.get("_job")  # TODO move to mixin
        self._gyms: Optional[List[SportGymData]] = None
        self._table: Optional[BeautifulSoup] = None

        super().__init__(*args, **kwargs)

    def start_requests(self) -> scrapy.Request:
        yield scrapy.Request(
            url=self.url,
            meta={"playwright": True},
        )

    @staticmethod
    def _get_section_address(section: Tag) -> str:
        return section.find("p").text

    @staticmethod
    def _get_section_name(section: Tag) -> str:
        return f'Zdrofit {section.find("a").text}'

    def _get_section_url(self, section: Tag) -> str:
        return f'https://{self._domain}{section.find("a")["href"].replace("//", "/")}'

    def _read_city(self, data: Tag) -> None:
        for section in data.find("ul"):
            self._gyms.append(
                SportGymData(
                    provider="zdrofit",
                    id=str(uuid.uuid4()),
                    url=self._get_section_url(section=section),
                    name=self._get_section_name(section=section),
                    address=self._get_section_address(section=section),
                )
            )

    def _read_gyms(self) -> None:
        for section in self._table.find_all("section"):
            self._read_city(data=section)

    def parse(self, response, **kwargs) -> dict:
        self._gyms = []

        table_html = response.selector.xpath('//*[@id="lista"]').get()
        self._table = BeautifulSoup(table_html, features="lxml")

        self._read_gyms()
        self.logger.info("aaa test")
        return {"gyms": self.gyms}

    @property
    def gyms(self) -> List[SportGymData]:
        if self._gyms is None:
            raise ValueError("read first")

        return self._gyms
