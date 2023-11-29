from __future__ import annotations

import datetime
import importlib.util
import uuid
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Iterator, Optional
from common.helpers import parse_duration_to_seconds
from common.constants import ScrapJobStatus


@dataclass
class ScrapJob:
    id: str
    spider: str
    status: ScrapJobStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime
    finished_at: Optional[datetime.datetime]

    @classmethod
    def new(cls, **data) -> ScrapJob:
        data["finished_at"] = None
        data["created_at"] = datetime.datetime.now()
        data["updated_at"] = datetime.datetime.now()
        data["status"] = ScrapJobStatus.PENDING.value

        return cls(id=str(uuid.uuid4()), **data)


@dataclass(frozen=True)
class SportClassData:
    name: str
    day: str
    end_hour: str
    start_hour: str


@dataclass(frozen=True)
class SportGymData:
    name: str
    address: str
    provider: str
    url: Optional[str]


@dataclass(frozen=True)
class JobSchedule:
    name: str
    job_method: str
    duration: str
    start_datetime: datetime.datetime

    @property
    def method(self) -> Any:
        data = self.job_method.split(".")
        module = importlib.import_module(".".join(data[:-1]))

        return getattr(module, data[-1])

    def _get_start_period_multiplier(self) -> int:
        _now = datetime.datetime.now()
        if self.start_datetime > _now:
            return 0
        else:
            return (datetime.datetime.now() - self.start_datetime).seconds // self.period + 1

    def execution_datetimes(self) -> Iterator[datetime.datetime]:
        n = self._get_start_period_multiplier()

        while True:
            yield self.start_datetime + n * datetime.timedelta(seconds=self.period)
            n += 1

    @classmethod
    def from_config(cls, **config) -> JobSchedule:
        now = datetime.datetime.now()
        hour, minute = (int(v) for v in config.get("start").split(":"))

        return cls(
            name=config.get("name"),
            job_method=config.get("job"),
            duration=config.get("duration"),
            start_datetime=datetime.datetime(year=now.year, month=now.month, day=now.day, hour=hour, minute=minute)
        )

    @cached_property
    def period(self) -> int:
        return parse_duration_to_seconds(duration=self.duration)