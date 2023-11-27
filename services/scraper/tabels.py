from piccolo.columns import Varchar, Timestamp, JSON
from piccolo.table import Table


class ScrapJob(Table):
    id = Varchar(length=64, primary_key=True)

    params = JSON()
    created_at = Timestamp()
    started_at = Timestamp()
    finished_at = Timestamp()
    spider_name = Varchar(length=128)
