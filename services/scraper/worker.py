from redis import Redis
from rq import Worker

import common  # type: ignore

# https://python-rq.org/docs/workers/#performance-notes
import scraper.jobs  # type: ignore
from scraper import settings


if __name__ == "__main__":
    w = Worker(['default'], connection=Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT))
    w.work()
    print('worker start')  # TODO logger
