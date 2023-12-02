from __future__ import annotations

import datetime
import random
import time
import uuid
from dataclasses import replace
from typing import Optional, Any

from common import constants
from common.entites import *
from common.entites import ScrapJob
from scraper.exceptions import (
    SpiderNotFinished,
)
from scraper.repositories import scrap_job_repository
from scraper.stores import redis_store
import asyncio


class SpiderDataConnector:
    MIN_READ_DELAY = 1
    MAX_READ_DELAY = 3
    MAX_READ_ATTEMPTS = 1000

    def __init__(self, spider_name: str, job_id: str) -> None:
        self._job_id = job_id
        self._spider_name = spider_name

    async def fetch_data(self) -> Optional[Any]:
        data = None
        read_attempts = 0
        while read_attempts < self.MAX_READ_ATTEMPTS:
            data = redis_store.retrieve(key=self.job_id)
            if data:
                break

            await asyncio.sleep(1)
            read_attempts += 1

        self._job_id = None
        if data is None:
            raise SpiderNotFinished(
                f"spider {self._spider_name}: no data within {self.MAX_READ_ATTEMPTS}"
            )

        return data

    @property
    def job_id(self) -> str:
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
        updated_data = {
            "status": status,
            "updated_at": datetime.datetime.now(),
        }
        if is_finished:
            updated_data["finished_at"] = datetime.datetime.now()

        self._job = replace(self._job, **updated_data)
        self.REPOSITORY.update(obj=self._job)

    @property
    def scrap_job(self) -> ScrapJob:
        return self._job
