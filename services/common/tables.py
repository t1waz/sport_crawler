from typing import List

from sqlalchemy import Column, String, JSON, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, Mapped, relationship

from common import constants

Base = declarative_base()


class ProviderTable(Base):
    __tablename__ = "provider"

    id = Column(String(64), primary_key=True)
    name = Column(String(48))
    gyms: Mapped[List["GymTable"]] = relationship(back_populates="provider")


class GymTable(Base):
    __tablename__ = "gym"

    id = Column(String(64), primary_key=True)
    address = Column(String(256))
    name = Column(String(48))
    url = Column(String(256))
    is_active = Boolean()
    provider_id: Mapped[str] = mapped_column(ForeignKey("provider.id"))
    provider: Mapped["ProviderTable"] = relationship(back_populates="gyms")
    classes: Mapped[List["GymClass"]] = relationship(back_populates="gym")


class GymClass(Base):
    __tablename__ = "gym_class"

    id = Column(String(64), primary_key=True)
    name = Column(String(48))
    gym_id: Mapped[str] = mapped_column(ForeignKey("gym.id"))
    gym: Mapped["GymTable"] = relationship(back_populates="classes")
    books: Mapped["GymClassBook"] = relationship(back_populates="gym_class")


class GymClassBook(Base):
    __tablename__ = "gym_class_book"

    id = Column(String(64), primary_key=True)
    is_active = Column(Boolean(), nullable=True)
    end_at = Column(DateTime(), nullable=True)
    start_at = Column(DateTime(), nullable=True)
    gym_class_id: Mapped[str] = mapped_column(ForeignKey("gym_class.id"))
    gym_class: Mapped["GymClass"] = relationship(back_populates="books")


class ScrapJobTable(Base):
    __tablename__ = "scrap_job"

    id = Column(String(64), primary_key=True)
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    spider_name = Column(String(64))
    params = Column(JSON(), default=[])
    finished_at = Column(DateTime(), nullable=True)
    status = Column(Enum(constants.ScrapJobStatus))
