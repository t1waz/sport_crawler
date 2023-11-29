import time

import httpx

from common import constants
from common.entites import ScrapJob
from scraper import settings
from scraper.repositories import scrap_job_repository
from common.redis import RedisStore
from redis import Redis


def run_spider(spider_name: str, job_id: str, **kwargs) -> None:
    response = httpx.post(f"http://{settings.CRAWLER_HOST}:{settings.CRAWLER_PORT}/schedule.json", data={"project": "crawler", "spider": spider_name, "jobid": job_id, **kwargs})
    print(response.status_code, response.text, '!!!!!!!!!!!!!!!')

    if response.status_code != 200:
        raise ValueError("network problem")  # TODO: custom exception
    # response.json.status = "error" -> invalid request

TIMEOUT = 10

def get_zdrofit_gyms():
    print('job')
    job = ScrapJob.new(spider="zdrofit_gym")
    job.status = constants.ScrapJobStatus.RUNNING.value
    scrap_job_repository.save(obj=job)

    redis_store = RedisStore(conn=Redis(host="redis", port=6379))
    try:
        run_spider(spider_name="zdrofit_gym", job_id=job.id, start_url="https://zdrofit.pl/grafik-zajec")
    except ValueError:
        job.status = constants.ScrapJobStatus.UNEXPECTED_ERROR.value
        scrap_job_repository.save(obj=job)

    data = None
    timeout_counter = 0
    while data is None:
        data = redis_store.retrieve(key=job.id)
        print('data is ', data)
        time.sleep(1)

    job.status = constants.ScrapJobStatus.FINISH.value
    scrap_job_repository.save(obj=job)
