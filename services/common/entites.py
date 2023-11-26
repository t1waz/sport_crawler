from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SportClassData:
    name: str
    day: str
    end_hour: str
    start_hour: str


@dataclass(frozen=True)
class SportGymData:
    name: str
    address: str
    provider: str
    url: Optional[str]
