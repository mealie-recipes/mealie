from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Tuple

from pydantic import BaseModel


@dataclass
class Cron:
    hours: int
    minutes: int

    @classmethod
    def parse(cls, time_str: str) -> Cron:
        time = time_str.split(":")
        return Cron(hours=int(time[0]), minutes=int(time[1]))


@dataclass
class ScheduledFunc(BaseModel):
    id: Tuple[str, int]
    name: str
    hour: int
    minutes: int
    callback: Callable

    max_instances: int = 1
    replace_existing: bool = True
    args: list = []
