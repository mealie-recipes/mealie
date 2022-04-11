from collections.abc import Callable
from dataclasses import dataclass, field

from pydantic import BaseModel


@dataclass(slots=True)
class ScheduledFunc(BaseModel):
    id: tuple[str, int]
    name: str
    hour: int
    minutes: int
    callback: Callable

    max_instances: int = 1
    replace_existing: bool = True
    args: list = field(default_factory=list)
