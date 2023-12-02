# from typing import Any
#
# from common import constants
# from scraper.exceptions import (
#     SpiderNotFinished,
#     SpiderNetworkException,
#     SpiderTimeoutException,
#     SpiderParseDataException,
# )
# from scraper.services import ScrapJobService, SpiderConnector
#
#
# class ScraperJobLogic:
#     SPIDER_NAME = ""
#
#     def __init__(self) -> None:
#         self._spider_connector = SpiderConnector(spider_name=self.SPIDER_NAME)
#         self._scrap_job_service = ScrapJobService.create_new(
#             spider_name=self.SPIDER_NAME
#         )
#
#     def get_spider_kwargs(self) -> dict:
#         raise NotImplemented
#
#     def process_data(self, data: Any) -> None:
#         raise NotImplemented
#
#     def run(self) -> None:
#         status = constants.ScrapJobStatus.RUNNING
#         self._scrap_job_service.update_status(status=status)
#
#         try:
#             self._spider_connector.trigger_spider(
#                 job_id=self._scrap_job_service.scrap_job.id, **self.get_spider_kwargs()
#             )
#         except SpiderNetworkException:
#             status = constants.ScrapJobStatus.NETWORK_ERROR
#         except SpiderNotFinished:
#             status = constants.ScrapJobStatus.SPIDER_NOT_FINISHED
#         except SpiderTimeoutException:
#             status = constants.ScrapJobStatus.NETWORK_ERROR
#         except SpiderParseDataException:
#             status = constants.ScrapJobStatus.CONTENT_ERROR
#         except Exception as exc:
#             print(f"get unknown exception {exc}")  # TODO: logger
#             status = constants.ScrapJobStatus.UNEXPECTED_ERROR
#
#         is_finished = status != constants.ScrapJobStatus.RUNNING
#         if is_finished:
#             self._scrap_job_service.update_status(
#                 status=status, is_finished=is_finished
#             )
#             return
#
#         try:
#             data = self._spider_connector.fetch_data()
#             status = constants.ScrapJobStatus.FINISH
#         except SpiderNotFinished:
#             status = constants.ScrapJobStatus.SPIDER_NOT_FINISHED
#             self._scrap_job_service.update_status(status=status, is_finished=True)
#             return
#
#         if not data:
#             status = constants.ScrapJobStatus.CONTENT_ERROR
#             self._scrap_job_service.update_status(status=status, is_finished=True)
#             return
#
#         try:
#             self.process_data(data=data)
#         except Exception as exc:
#             print(f"got exception {exc} during process data {data}")  # TODO: logger
#             status = constants.ScrapJobStatus.PROCESS_DATA_ERROR
#
#         self._scrap_job_service.update_status(status=status, is_finished=True)
