from functools import lru_cache
from typing import Protocol

from passlib.context import CryptContext

from mealie.core.config import get_app_settings


class Hasher(Protocol):
    def hash(self, password: str) -> str:
        ...

    def verify(self, password: str, hashed: str) -> bool:
        ...


class FakeHasher:
    def hash(self, password: str) -> str:
        return password

    def verify(self, password: str, hashed: str) -> bool:
        return password == hashed


class PasslibHasher:
    def __init__(self) -> None:
        self.ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self.ctx.hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        return self.ctx.verify(password, hashed)


@lru_cache(maxsize=1)
def get_hasher() -> Hasher:
    settings = get_app_settings()

    if settings.TESTING:
        return FakeHasher()

    return PasslibHasher()
