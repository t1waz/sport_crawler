from piccolo.table import Table
from piccolo.columns import Varchar, ForeignKey, Timestamp


class Gym(Table):
    id = Varchar(length=64, primary_key=True)

    address = Varchar(length=256)
    name = Varchar(length=48, unique=True)
    url = Varchar(length=256, unique=True)


class GymClass(Table):
    id = Varchar(length=64, primary_key=True)

    gym = ForeignKey(references=Gym)
    name = Varchar(length=48, unique=True)


class GymClassBook(Table):
    id = Varchar(length=64, primary_key=True)

    end_datetime = Timestamp()
    start_datetime = Timestamp()
    gym_class = ForeignKey(references=GymClass)
