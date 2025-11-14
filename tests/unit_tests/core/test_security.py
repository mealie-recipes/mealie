from pytest import MonkeyPatch

from mealie.core.config import get_app_settings
from mealie.core.security.hasher import BcryptHasher, FakeHasher, get_hasher
from tests.utils.factories import random_string


def clear_hasher_cache():
    get_hasher.cache_clear()
    get_app_settings.cache_clear()


def test_get_hasher(monkeypatch: MonkeyPatch):
    try:
        hasher = get_hasher()
        assert isinstance(hasher, FakeHasher)

        monkeypatch.setenv("TESTING", "0")
        clear_hasher_cache()

        hasher = get_hasher()
        assert isinstance(hasher, BcryptHasher)
    finally:
        clear_hasher_cache()


def test_hasher_long_password(monkeypatch: MonkeyPatch):
    try:
        monkeypatch.setenv("TESTING", "0")
        clear_hasher_cache()

        hasher = get_hasher()
        assert isinstance(hasher, BcryptHasher)

        # Create a very long password which bcrypt doesn't support
        password = random_string(256)
        assert len(password) > 72

        # Make sure our hasher still works even though the password is too long
        hashed_password = hasher.hash(password)
        assert hashed_password
        assert hasher.verify(password, hashed_password)
    finally:
        clear_hasher_cache()
