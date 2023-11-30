from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped
from typing import List
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column

from sqlalchemy import ForeignKey

Base = declarative_base()


class ProviderTable(Base):
    __tablename__ = 'provider'

    id = Column(String(64), primary_key=True)
    name = Column(String(48))
    gyms: Mapped[List["GymTable"]] = relationship(back_populates="provider")


class GymTable(Base):
    __tablename__ = 'gym_table'

    id = Column(String(64), primary_key=True)
    address = Column(String(256))
    name = Column(String(48))
    url = Column(String(256))
    is_active = Boolean()
    provider_id: Mapped[str] = mapped_column(ForeignKey("provider.id"))
    provider: Mapped["ProviderTable"] = relationship(back_populates="gyms")


# class GymTable(Table):
#     id = Varchar(length=64, primary_key=True)
#     address = Varchar(length=256)
#     name = Varchar(length=48, unique=True)
#     url = Varchar(length=256, unique=True)
#     provider = ForeignKey(references=ProviderTable)
#     is_active = Boolean(default=True)
#
#
# class GymClassTable(Table):
#     id = Varchar(length=64, primary_key=True)
#     gym = ForeignKey(references=GymTable)
#     name = Varchar(length=48, unique=True)
#
#
# class GymClassBookTable(Table):
#     id = Varchar(length=64, primary_key=True)
#     end_datetime = Timestamp()
#     start_datetime = Timestamp()
#     gym_class = ForeignKey(references=GymClassTable)
