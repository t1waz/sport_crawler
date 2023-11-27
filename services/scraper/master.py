from __future__ import annotations

import datetime
import importlib.util
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterator, List

import yaml
from redis import Redis
from rq import Queue

from scraper import settings


def load_schedule_config(schedule_file_path: str) -> dict:
    with open(schedule_file_path, "r") as file:
        data = file.read()

    return yaml.safe_load(data)


def parse_duration_to_seconds(duration: str) -> int:
    duration = duration.lower()
    if duration.endswith("h"):
        base = 3600
    elif duration.endswith("m"):
        base = 60
    elif duration.endswith("s"):
        base = 1
    else:
        base = 1

    return int(duration.strip("h").strip("m").strip("s")) * base


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

    def execution_datetimes(self) -> Iterator[datetime.datetime]:
        period = parse_duration_to_seconds(duration=self.duration)
        now = datetime.datetime.now()
        if self.start_datetime < now:
            i = (datetime.datetime.now() - self.start_datetime).seconds // period + 1
        else:
            i = 0

        while True:
            yield self.start_datetime + i * datetime.timedelta(seconds=period)
            i += 1

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


@lru_cache
def get_schedule() -> dict:
    return load_schedule_config(schedule_file_path=settings.SCHEDULE_PATH)


schedule_config = get_schedule()


if __name__ == "__main__":
    redis_q = Queue(connection=Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT))
    jobs = [JobSchedule.from_config(**config) for config in schedule_config.get("jobs", [])]
    data = [[job, next(job.execution_datetimes())] for job in jobs]

    while True:
        now = datetime.datetime.now()  # TODO make warsaw UTC aware
        for i, (job, execution_datetime) in enumerate(data):
            if now > execution_datetime:
                print(f"running job {job.name}")  # TODO logger
                redis_q.enqueue(job.method)
                data[i][1] = next(job.execution_datetimes())

        time.sleep(1)
