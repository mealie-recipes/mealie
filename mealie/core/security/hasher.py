from functools import lru_cache
from typing import Protocol

import bcrypt

from mealie.core.config import get_app_settings


class Hasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, hashed: str) -> bool: ...


class FakeHasher:
    def hash(self, password: str) -> str:
        return password

    def verify(self, password: str, hashed: str) -> bool:
        return password == hashed


class BcryptHasher:
    def hash(self, password: str) -> str:
        password_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verify(self, password: str, hashed: str) -> bool:
        password_bytes = password.encode("utf-8")
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)


@lru_cache(maxsize=1)
def get_hasher() -> Hasher:
    settings = get_app_settings()

    if settings.TESTING:
        return FakeHasher()

    return BcryptHasher()
