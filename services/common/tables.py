from typing import List

from sqlalchemy import Column, String, JSON, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, Mapped, relationship

from common import constants

Base = declarative_base()


class ProviderTable(Base):
    __tablename__ = 'provider'

    id = Column(String(64), primary_key=True)
    name = Column(String(48))
    gyms: Mapped[List["GymTable"]] = relationship(back_populates="provider")


class GymTable(Base):
    __tablename__ = 'gym'

    id = Column(String(64), primary_key=True)
    address = Column(String(256))
    name = Column(String(48))
    url = Column(String(256))
    is_active = Boolean()
    provider_id: Mapped[str] = mapped_column(ForeignKey("provider.id"))
    provider: Mapped["ProviderTable"] = relationship(back_populates="gyms")


class ScrapJobTable(Base):
    __tablename__ = "scrap_job"

    id = Column(String(64), primary_key=True)
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    spider_name = Column(String(64))
    params = Column(JSON(), default=[])
    finished_at = Column(DateTime(), nullable=True)
    status = Column(Enum(constants.ScrapJobStatus))


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
