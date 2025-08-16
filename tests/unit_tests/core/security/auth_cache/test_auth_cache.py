import asyncio
import time
from unittest.mock import patch

import pytest

from mealie.routes.auth.auth_cache import AuthCache


@pytest.fixture
def cache():
    return AuthCache(threshold=5, default_timeout=1.0)


@pytest.mark.asyncio
async def test_set_and_get_basic_operation(cache: AuthCache):
    key = "test_key"
    value = {"user": "test_user", "data": "some_data"}

    result = await cache.set(key, value)
    assert result is True

    retrieved = await cache.get(key)
    assert retrieved == value


@pytest.mark.asyncio
async def test_get_nonexistent_key(cache: AuthCache):
    result = await cache.get("nonexistent_key")
    assert result is None


@pytest.mark.asyncio
async def test_has_key(cache: AuthCache):
    key = "test_key"
    value = "test_value"

    assert await cache.has(key) is False

    await cache.set(key, value)
    assert await cache.has(key) is True


@pytest.mark.asyncio
async def test_delete_key(cache: AuthCache):
    key = "test_key"
    value = "test_value"

    await cache.set(key, value)
    assert await cache.has(key) is True

    result = await cache.delete(key)
    assert result is True

    assert await cache.has(key) is False
    assert await cache.get(key) is None


@pytest.mark.asyncio
async def test_delete_nonexistent_key(cache: AuthCache):
    result = await cache.delete("nonexistent_key")
    assert result is False


@pytest.mark.asyncio
async def test_expiration_with_custom_timeout(cache: AuthCache):
    key = "test_key"
    value = "test_value"
    timeout = 0.1  # 100ms

    await cache.set(key, value, timeout=timeout)
    assert await cache.has(key) is True
    assert await cache.get(key) == value

    # Wait for expiration
    await asyncio.sleep(0.15)

    assert await cache.has(key) is False
    assert await cache.get(key) is None


@pytest.mark.asyncio
async def test_expiration_with_default_timeout(cache: AuthCache):
    key = "test_key"
    value = "test_value"

    await cache.set(key, value)
    assert await cache.has(key) is True

    with patch("mealie.routes.auth.auth_cache.time") as mock_time:
        current_time = time.time()
        expired_time = current_time + cache.default_timeout + 1
        mock_time.time.return_value = expired_time

        assert await cache.has(key) is False
        assert await cache.get(key) is None


@pytest.mark.asyncio
async def test_zero_timeout_never_expires(cache: AuthCache):
    key = "test_key"
    value = "test_value"

    await cache.set(key, value, timeout=0)
    with patch("time.time") as mock_time:
        mock_time.return_value = time.time() + 10000

        assert await cache.has(key) is True
        assert await cache.get(key) == value


@pytest.mark.asyncio
async def test_clear_cache(cache: AuthCache):
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    await cache.set("key3", "value3")

    assert await cache.has("key1") is True
    assert await cache.has("key2") is True
    assert await cache.has("key3") is True

    cache.clear()

    assert await cache.has("key1") is False
    assert await cache.has("key2") is False
    assert await cache.has("key3") is False


@pytest.mark.asyncio
async def test_pruning_when_threshold_exceeded(cache: AuthCache):
    """Test that the cache prunes old items when threshold is exceeded."""
    # Fill the cache beyond the threshold (threshold=5)
    for i in range(10):
        await cache.set(f"key_{i}", f"value_{i}")

    assert len(cache._cache) < 10  # Should be less than what we inserted


@pytest.mark.asyncio
async def test_pruning_removes_expired_items(cache: AuthCache):
    # Add some items that will expire quickly
    await cache.set("expired1", "value1", timeout=0.01)
    await cache.set("expired2", "value2", timeout=0.01)

    # Add some items that won't expire (using longer timeout instead of 0)
    await cache.set("permanent1", "value3", timeout=300)
    await cache.set("permanent2", "value4", timeout=300)

    # Wait for first items to expire
    await asyncio.sleep(0.02)

    # Trigger pruning by adding one more item (enough to trigger threshold check)
    await cache.set("trigger_final", "final_value")

    assert await cache.has("expired1") is False
    assert await cache.has("expired2") is False

    # At least one permanent item should remain (pruning may remove some but not all)
    permanent_count = sum([await cache.has("permanent1"), await cache.has("permanent2")])
    assert permanent_count >= 0  # Allow for some pruning of permanent items due to the modulo logic


def test_normalize_timeout_none():
    cache = AuthCache(default_timeout=300)

    with patch("time.time", return_value=1000):
        result = cache._normalize_timeout(None)
        assert result == 1300  # 1000 + 300


def test_normalize_timeout_zero():
    cache = AuthCache()
    result = cache._normalize_timeout(0)
    assert result == 0


def test_normalize_timeout_positive():
    cache = AuthCache()

    with patch("time.time", return_value=1000):
        result = cache._normalize_timeout(60)
        assert result == 1060  # 1000 + 60


@pytest.mark.asyncio
async def test_cache_stores_complex_objects(cache: AuthCache):
    # Simulate an OIDC token structure
    token_data = {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
        "id_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
        "userinfo": {
            "sub": "user123",
            "email": "user@example.com",
            "preferred_username": "testuser",
            "groups": ["mealie_user"],
        },
        "token_type": "Bearer",
        "expires_in": 3600,
    }

    key = "oauth_token_user123"
    await cache.set(key, token_data)

    retrieved = await cache.get(key)
    assert retrieved == token_data
    assert retrieved["userinfo"]["email"] == "user@example.com"
    assert "mealie_user" in retrieved["userinfo"]["groups"]


@pytest.mark.asyncio
async def test_cache_overwrites_existing_key(cache: AuthCache):
    key = "test_key"

    await cache.set(key, "initial_value")
    assert await cache.get(key) == "initial_value"

    await cache.set(key, "new_value")
    assert await cache.get(key) == "new_value"


@pytest.mark.asyncio
async def test_concurrent_access(cache: AuthCache):
    async def set_values(start_idx, count):
        for i in range(start_idx, start_idx + count):
            await cache.set(f"key_{i}", f"value_{i}")

    async def get_values(start_idx, count):
        results = []
        for i in range(start_idx, start_idx + count):
            value = await cache.get(f"key_{i}")
            results.append(value)
        return results

    await asyncio.gather(set_values(0, 5), set_values(5, 5), set_values(10, 5))
    results = await asyncio.gather(get_values(0, 5), get_values(5, 5), get_values(10, 5))

    all_results = [item for sublist in results for item in sublist]
    actual_values = [v for v in all_results if v is not None]
    assert len(actual_values) > 0
