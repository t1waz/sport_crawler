from __future__ import annotations

import time  # noqa

from common.entites import JobSchedule
from common.helpers import load_schedule_config
from common.tables import Base
from scraper import settings as scraper_settings
from scraper.db import engine  # noqa
from scraper.jobs import *  # noqa


if __name__ == "__main__":
    Base.metadata.create_all(engine)

    schedule_config = load_schedule_config(
        schedule_file_path=scraper_settings.SCHEDULE_CONFIG_PATH
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
                print(f"schedule job {job.name}")  # TODO logger
                job.method.send()
                data[i][1] = next(job.execution_datetimes())

        time.sleep(1)
