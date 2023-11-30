from functools import lru_cache

from common.repositores import SQLRepository
from common.tables import ScrapJobTable
from scraper.db import engine


class ScrapJobRepository(SQLRepository):
    TABLE = ScrapJobTable


@lru_cache
def get_scrap_job_repository() -> ScrapJobRepository:
    return ScrapJobRepository(engine=engine)


scrap_job_repository = get_scrap_job_repository()
