from piccolo.table import Table
from piccolo.columns import Varchar, ForeignKey, Timestamp


class ScrapJobTable(Table):
    id = Varchar(length=64, primary_key=True)
    created_at = Timestamp()
    updated_at = Timestamp()
    status = Varchar(length=48)
    spider = Varchar(length=128)
    finished_at = Timestamp(null=True)


class ProviderTable(Table):
    id = Varchar(length=64, primary_key=True)
    name = Varchar(length=48, unique=True)


class GymTable(Table):
    id = Varchar(length=64, primary_key=True)
    address = Varchar(length=256)
    name = Varchar(length=48, unique=True)
    url = Varchar(length=256, unique=True)
    provider = ForeignKey(references=ProviderTable)


class GymClassTable(Table):
    id = Varchar(length=64, primary_key=True)
    gym = ForeignKey(references=GymTable)
    name = Varchar(length=48, unique=True)


class GymClassBookTable(Table):
    id = Varchar(length=64, primary_key=True)
    end_datetime = Timestamp()
    start_datetime = Timestamp()
    gym_class = ForeignKey(references=GymClassTable)
