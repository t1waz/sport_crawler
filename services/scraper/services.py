from __future__ import annotations

import datetime
import uuid
from dataclasses import replace
from typing import Optional

from common import constants
from common.entites import ScrapJob
from scraper.repositories import scrap_job_repository


class ScrapJobService:
    REPOSITORY = scrap_job_repository

    def __init__(
        self,
        scrap_job: ScrapJob,
    ) -> None:
        self._job = scrap_job

    @classmethod
    def create_new(
        cls, name: str, status: Optional[constants.ScrapJobStatus] = None
    ) -> ScrapJobService:
        status = status or constants.ScrapJobStatus.PENDING

        scrap_job = ScrapJob(
            name=name,
            status=status,
            finished_at=None,
            id=str(uuid.uuid4()),
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )
        cls.REPOSITORY.save(obj=scrap_job)

        return cls(scrap_job=scrap_job)

    def update_status(
        self,
        status: constants.ScrapJobStatus,
        data: Optional[str] = None,
        is_finished: Optional[bool] = False,
    ) -> None:
        updated_data = {
            "status": status,
            "updated_at": datetime.datetime.now(),
        }
        if is_finished:
            updated_data["finished_at"] = datetime.datetime.now()
        if data:
            updated_data["data"] = data

        self._job = replace(self._job, **updated_data)
        self.REPOSITORY.update(obj=self._job)

    @property
    def scrap_job(self) -> ScrapJob:
        return self._job
