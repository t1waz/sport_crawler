import traceback
from typing import Any, Optional

from common import constants
from scraper.grpc_clients import get_website_fetcher_client
from scraper.services import ScrapJobService


class ScraperJobLogic:
    JOB_NAME = ""

    def __init__(self) -> None:
        self._fetch_client = get_website_fetcher_client()
        self._scrap_job_service = ScrapJobService.create_new(name=self.JOB_NAME)

    def process_data(self, page_data: str) -> Optional[Any]:
        raise NotImplemented()

    def run(self) -> Any:
        """
        call this to scrap data
        """
        print(f"start job for {self.JOB_NAME}")  # TODO: logger
        try:
            page_data = self._fetch_client.fetch_page(url=self.url)
        except Exception as _:  # noqa
            self._scrap_job_service.update_status(
                is_finished=True,
                data=traceback.format_exc(),
                status=constants.ScrapJobStatus.FETCHER_NOT_FINISHED,
            )
            return None

        try:
            data = self.process_data(page_data=page_data)
        except Exception as _:  # noqa
            self._scrap_job_service.update_status(
                is_finished=True,
                data=traceback.format_exc(),
                status=constants.ScrapJobStatus.PROCESS_DATA_ERROR,
            )
            return

        self._scrap_job_service.update_status(
            is_finished=True, status=constants.ScrapJobStatus.FINISH
        )
        print(f"job for {self.JOB_NAME} sucess")  # TODO: logger

        return data

    @property
    def url(self) -> str:
        raise NotImplemented()
