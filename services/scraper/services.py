from __future__ import annotations

import datetime
import time
import uuid
from dataclasses import replace
from typing import Optional, Any

import httpx

from common import constants
from common.entites import ScrapJob
from scraper import settings
from scraper.exceptions import (
    SpiderTimeoutException,
    SpiderNetworkException,
    SpiderNotFinished,
)
from scraper.repositories import scrap_job_repository
from scraper.stores import redis_store
import random


class SpiderConnector:
    MIN_READ_DELAY = 1
    MAX_READ_DELAY = 3
    MAX_READ_ATTEMPTS = 1000

    def __init__(self, spider_name: str) -> None:
        self._spider_name = spider_name
        self._job_id: Optional[str] = None
        self._response: Optional[httpx.Response] = None

    def fetch_data(self) -> Optional[Any]:
        data = None
        read_attempts = 0
        while read_attempts < self.MAX_READ_ATTEMPTS:
            data = redis_store.retrieve(key=self.job_id)
            if data:
                break

            time.sleep(random.randint(self.MIN_READ_DELAY, self.MAX_READ_ATTEMPTS))
            read_attempts += 1

        self._job_id = None
        if data is None:
            raise SpiderNotFinished(
                f"spider {self._spider_name}: no data within {self.MAX_READ_ATTEMPTS}"
            )

        return data

    def trigger_spider(self, job_id: str, **data) -> None:
        self._job_id = job_id

        try:
            self._response = httpx.post(
                f"http://{settings.CRAWLER_HOST}:{settings.CRAWLER_PORT}/schedule.json",
                data={
                    "jobid": job_id,
                    "project": "crawler",
                    "spider": self._spider_name,
                    **data,
                },
            )
        except httpx.TimeoutException:
            raise SpiderTimeoutException("spider timeout")

        if self._response.status_code != 200:
            raise SpiderNetworkException("response is not 200")

        data = self._response.json()

        # if data.get("status") == "error":
        #

    @property
    def job_id(self) -> Optional[str]:
        if self._job_id is None:
            raise ValueError("trigger spider first")

        return self._job_id


class ScrapJobService:
    REPOSITORY = scrap_job_repository

    def __init__(
        self,
        scrap_job: ScrapJob,
    ) -> None:
        self._job = scrap_job

    @classmethod
    def create_new(
        cls, spider_name: str, status: Optional[constants.ScrapJobStatus] = None
    ) -> ScrapJobService:
        status = status or constants.ScrapJobStatus.PENDING

        scrap_job = ScrapJob(
            status=status,
            finished_at=None,
            id=str(uuid.uuid4()),
            spider_name=spider_name,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )
        cls.REPOSITORY.save(obj=scrap_job)

        return cls(scrap_job=scrap_job)

    def update_status(
        self, status: constants.ScrapJobStatus, is_finished: Optional[bool] = False
    ) -> None:
        updated_data = {"status": status}
        if is_finished:
            updated_data["finished_at"] = datetime.datetime.now()

        self._job = replace(self._job, **updated_data)
        self.REPOSITORY.update(obj=self._job)

    @property
    def scrap_job(self) -> ScrapJob:
        return self._job
