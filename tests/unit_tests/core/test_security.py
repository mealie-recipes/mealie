from pytest import MonkeyPatch

from mealie.core.config import get_app_settings
from mealie.core.security.hasher import FakeHasher, PasslibHasher, get_hasher


def test_get_hasher(monkeypatch: MonkeyPatch):
    hasher = get_hasher()

    assert isinstance(hasher, FakeHasher)

    monkeypatch.setenv("TESTING", "0")

    get_hasher.cache_clear()
    get_app_settings.cache_clear()

    hasher = get_hasher()

    assert isinstance(hasher, PasslibHasher)

    get_app_settings.cache_clear()
    get_hasher.cache_clear()
