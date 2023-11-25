from dataclasses import dataclass


@dataclass(frozen=True)
class SportClassData:
    name: str
    day: str
    end_hour: str
    start_hour: str
