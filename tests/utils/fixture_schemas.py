from dataclasses import dataclass
from typing import Any


@dataclass
class TestUser:
    user_id: int
    group_id: int
    token: Any
