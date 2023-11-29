from __future__ import annotations

import datetime
import time

from redis import Redis
from rq import Queue

from common.entites import JobSchedule
from common.helpers import load_schedule_config
from scraper import settings


if __name__ == "__main__":
    schedule_config = load_schedule_config(
        schedule_file_path=settings.SCHEDULE_CONFIG_PATH
    )
    redis_q = Queue(
        connection=Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    )
    jobs = [
        JobSchedule.from_config(**config) for config in schedule_config.get("jobs", [])
    ]

    data = [[job, next(job.execution_datetimes())] for job in jobs]

    print("started master")  # TODO logger

    while True:
        now = datetime.datetime.now()  # TODO make warsaw UTC aware
        for i, (job, execution_datetime) in enumerate(data):
            if now > execution_datetime:
                print(f"running job {job.name}")  # TODO logger
                redis_q.enqueue(job.method)
                data[i][1] = next(job.execution_datetimes())

        time.sleep(1)
