from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from mealie.core.dependencies.dependencies import validate_long_live_token


class FakeSession:
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


class FakeApiTokenRepo:
    def __init__(self, tokens):
        self.tokens = tokens
        self.query = None

    def multi_query(self, query):
        self.query = query
        return self.tokens


def test_validate_long_live_token_commits_after_successful_lookup(monkeypatch):
    session = FakeSession()
    user = SimpleNamespace(id="user-id")
    api_tokens = FakeApiTokenRepo([SimpleNamespace(user=user)])

    monkeypatch.setattr(
        "mealie.core.dependencies.dependencies.get_repositories",
        lambda session, group_id, household_id: SimpleNamespace(api_tokens=api_tokens),
    )

    assert validate_long_live_token(session, "client-token", "user-id") is user
    assert api_tokens.query == {"token": "client-token", "user_id": "user-id"}
    assert session.committed is True
    assert session.rolled_back is False


def test_validate_long_live_token_rolls_back_after_failed_lookup(monkeypatch):
    session = FakeSession()
    api_tokens = FakeApiTokenRepo([])

    monkeypatch.setattr(
        "mealie.core.dependencies.dependencies.get_repositories",
        lambda session, group_id, household_id: SimpleNamespace(api_tokens=api_tokens),
    )

    with pytest.raises(HTTPException):
        validate_long_live_token(session, "client-token", "user-id")

    assert session.committed is False
    assert session.rolled_back is True
