from typing import List, Optional

import scrapy
from bs4 import BeautifulSoup
from bs4.element import Tag

from common.entites import SportGymData


class ZdrofitGymSpider(scrapy.Spider):
    """
    Read all Zdrofit gyms (places).
    """

    name = "zdrofit_gym"

    def __init__(self, *args, **kwargs) -> None:
        self.url = kwargs.get("start_url") or "https://zdrofit.pl/grafik-zajec"
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
        try:
            return f'Zdrofit {section.find("a").text}'
        except Exception as exc:
            print(section, "!!!")
            raise exc

    def _read_city(self, data: Tag) -> None:
        for section in data.find("ul"):
            self._gyms.append(
                SportGymData(
                    url=None,
                    provider="zdrofit",
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

        return {"gyms": self.gyms}

    @property
    def gyms(self) -> List[SportGymData]:
        if self._gyms is None:
            raise ValueError("read first")

        return self._gyms
