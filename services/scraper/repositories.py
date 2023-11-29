from functools import lru_cache

from pymongo import MongoClient

from common.repositores import MongoRepository
from scraper import settings


class ScrapJobRepository(MongoRepository):
    COLLECTION_NAME = "scrap-job"


@lru_cache
def get_scrap_job_repository() -> ScrapJobRepository:
    return ScrapJobRepository(
        db=MongoClient(host=settings.MONGO_HOST, port=settings.MONGO_PORT)[
            settings.MONGO_DATABASE
        ]
    )


scrap_job_repository = get_scrap_job_repository()
