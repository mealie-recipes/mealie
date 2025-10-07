from functools import lru_cache
from typing import Protocol

import bcrypt

from mealie.core import root_logger
from mealie.core.config import get_app_settings

logger = root_logger.get_logger()


class Hasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, hashed: str) -> bool: ...


class FakeHasher:
    def hash(self, password: str) -> str:
        return password

    def verify(self, password: str, hashed: str) -> bool:
        return password == hashed


class BcryptHasher:
    def _get_password_bytes(self, password: str) -> bytes:
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            logger.warning(
                "Password is longer than 72 bytes, which bcrypt does not support. "
                "Manually truncating password to 72 bytes. Consider using a shorter password."
            )
            password_bytes = password_bytes[:72]

        return password_bytes

    def hash(self, password: str) -> str:
        password_bytes = self._get_password_bytes(password)
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verify(self, password: str, hashed: str) -> bool:
        password_bytes = self._get_password_bytes(password)
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)


@lru_cache(maxsize=1)
def get_hasher() -> Hasher:
    settings = get_app_settings()

    if settings.TESTING:
        return FakeHasher()

    return BcryptHasher()
