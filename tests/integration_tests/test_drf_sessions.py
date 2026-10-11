import os
from unittest.mock import Mock

import django
import pytest
from django.test import Client

from mealie.db import db_setup


@pytest.mark.parametrize(
    "path",
    [
        "/api/app/about",
        "/api/app/about/startup-info",
    ],
)
@pytest.mark.parametrize("fail_query", [False, True])
def test_drf_about_closes_session(monkeypatch, path, fail_query):
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "mealie.drf_api.settings",
    )
    django.setup()

    from mealie.drf_api import views

    original_factory = db_setup.SessionLocal
    close_spies = []

    def create_session():
        session = original_factory()
        close_spy = Mock(wraps=session.close)
        monkeypatch.setattr(session, "close", close_spy)
        close_spies.append(close_spy)

        if fail_query and path.endswith("/startup-info"):
            monkeypatch.setattr(
                session,
                "query",
                Mock(side_effect=RuntimeError("simulated database failure")),
            )

        return session

    monkeypatch.setattr(db_setup, "SessionLocal", create_session)

    if fail_query and path == "/api/app/about":
        monkeypatch.setattr(
            views,
            "get_repositories",
            Mock(side_effect=RuntimeError("simulated database failure")),
        )

    client = Client()

    if fail_query:
        with pytest.raises(RuntimeError, match="simulated database failure"):
            client.get(path)
    else:
        response = client.get(path)
        assert response.status_code == 200

    assert len(close_spies) == 1
    close_spies[0].assert_called_once_with()
