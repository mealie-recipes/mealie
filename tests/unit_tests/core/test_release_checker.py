from unittest.mock import MagicMock

import pytest
import requests

from mealie.core import release_checker


@pytest.fixture(autouse=True)
def reset_cache():
    release_checker.get_latest_github_release.cache_clear()
    release_checker._LAST_RESET = None
    yield
    release_checker.get_latest_github_release.cache_clear()
    release_checker._LAST_RESET = None


def test_latest_version_request_has_a_timeout(monkeypatch: pytest.MonkeyPatch):
    response = MagicMock()
    response.json.return_value = {"tag_name": "v9.9.9"}
    mock_get = MagicMock(return_value=response)
    monkeypatch.setattr(release_checker.requests, "get", mock_get)

    assert release_checker.get_latest_version() == "v9.9.9"
    assert mock_get.call_args.kwargs.get("timeout")


def test_unreachable_github_is_not_retried_on_every_call(monkeypatch: pytest.MonkeyPatch):
    mock_get = MagicMock(side_effect=requests.ConnectionError())
    monkeypatch.setattr(release_checker.requests, "get", mock_get)

    assert release_checker.get_latest_version() == "error fetching version"
    assert release_checker.get_latest_version() == "error fetching version"
    assert mock_get.call_count == 1
