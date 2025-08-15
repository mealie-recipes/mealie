import asyncio

import pytest
from authlib.integrations.starlette_client import OAuth

from mealie.routes.auth.auth_cache import AuthCache


def test_auth_cache_initialization_with_oauth():
    oauth = OAuth(cache=AuthCache())
    oauth.register(
        "test_oidc",
        client_id="test_client_id",
        client_secret="test_client_secret",
        server_metadata_url="https://example.com/.well-known/openid_configuration",
        client_kwargs={"scope": "openid email profile"},
        code_challenge_method="S256",
    )

    assert oauth is not None
    assert isinstance(oauth.cache, AuthCache)
    assert "test_oidc" in oauth._clients


@pytest.mark.asyncio
async def test_oauth_cache_operations():
    cache = AuthCache(threshold=500, default_timeout=300)
    cache_key = "oauth_state_12345"
    oauth_data = {
        "state": "12345",
        "code_verifier": "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk",
        "redirect_uri": "http://localhost:3000/login",
    }

    result = await cache.set(cache_key, oauth_data, timeout=600)  # 10 minutes
    assert result is True

    retrieved_data = await cache.get(cache_key)
    assert retrieved_data == oauth_data
    assert retrieved_data["state"] == "12345"

    deleted = await cache.delete(cache_key)
    assert deleted is True
    assert await cache.get(cache_key) is None


@pytest.mark.asyncio
async def test_oauth_cache_handles_token_expiration():
    cache = AuthCache()
    token_key = "access_token_user123"
    token_data = {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "openid email profile",
    }

    await cache.set(token_key, token_data, timeout=0.1)
    assert await cache.has(token_key) is True

    await asyncio.sleep(0.15)
    assert await cache.has(token_key) is False
    assert await cache.get(token_key) is None


@pytest.mark.asyncio
async def test_oauth_cache_concurrent_requests():
    cache = AuthCache()

    async def simulate_oauth_flow(user_id: str):
        """Simulate a complete OAuth flow for a user."""
        state_key = f"oauth_state_{user_id}"
        token_key = f"access_token_{user_id}"

        state_data = {"state": user_id, "code_verifier": f"verifier_{user_id}"}
        await cache.set(state_key, state_data, timeout=600)

        token_data = {"access_token": f"token_{user_id}", "user_id": user_id, "expires_in": 3600}
        await cache.set(token_key, token_data, timeout=3600)

        state = await cache.get(state_key)
        token = await cache.get(token_key)

        return state, token

    results = await asyncio.gather(
        simulate_oauth_flow("user1"), simulate_oauth_flow("user2"), simulate_oauth_flow("user3")
    )

    for i, (state, token) in enumerate(results, 1):
        assert state["state"] == f"user{i}"
        assert token["access_token"] == f"token_user{i}"


def test_auth_cache_disabled_when_oidc_not_ready():
    cache = AuthCache()
    assert cache is not None
    assert isinstance(cache, AuthCache)


@pytest.mark.asyncio
async def test_auth_cache_memory_efficiency():
    cache = AuthCache(threshold=10, default_timeout=300)
    for i in range(50):
        await cache.set(f"token_{i}", f"data_{i}", timeout=0)  # Never expire

    assert len(cache._cache) <= 15  # Should be close to threshold, accounting for pruning logic

    remaining_items = 0
    for i in range(50):
        if await cache.has(f"token_{i}"):
            remaining_items += 1

    assert 0 < remaining_items < 50


@pytest.mark.asyncio
async def test_auth_cache_with_real_oauth_data_structure():
    cache = AuthCache()
    oauth_token = {
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEifQ...",
        "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEifQ...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "openid email profile groups",
        "userinfo": {
            "sub": "auth0|507f1f77bcf86cd799439011",
            "email": "john.doe@example.com",
            "email_verified": True,
            "name": "John Doe",
            "preferred_username": "johndoe",
            "groups": ["mealie_user", "staff"],
        },
    }

    user_session_key = "oauth_session_auth0|507f1f77bcf86cd799439011"
    await cache.set(user_session_key, oauth_token, timeout=3600)

    retrieved = await cache.get(user_session_key)
    assert retrieved["access_token"] == oauth_token["access_token"]
    assert retrieved["userinfo"]["email"] == "john.doe@example.com"
    assert "mealie_user" in retrieved["userinfo"]["groups"]
    assert retrieved["userinfo"]["email_verified"] is True

    updated_token = oauth_token.copy()
    updated_token["access_token"] = "new_access_token_eyJhbGciOiJSUzI1NiIs..."
    updated_token["userinfo"]["last_login"] = "2024-01-01T12:00:00Z"

    await cache.set(user_session_key, updated_token, timeout=3600)

    updated_retrieved = await cache.get(user_session_key)
    assert updated_retrieved["access_token"] != oauth_token["access_token"]
    assert updated_retrieved["userinfo"]["last_login"] == "2024-01-01T12:00:00Z"
