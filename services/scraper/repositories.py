from common.tables import ScrapJobTable
from common.entites import ScrapJob
from dataclasses import asdict


class ScrapJobRepository:
    TABLE = ScrapJobTable

    @classmethod
    def save(cls, obj: ScrapJob) -> None:
        table_record = cls.TABLE(**asdict(obj))
        table_record.save().run_sync()


scrap_job_repository = ScrapJobRepository()
