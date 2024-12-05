import datetime
from functools import lru_cache

import requests

_LAST_RESET: datetime.datetime | None = None


@lru_cache(maxsize=1)
def get_latest_github_release() -> str:
    """
    Gets the latest release from GitHub.

    Returns:
        str: The latest release from GitHub.
    """

    url = "https://api.github.com/repos/hay-kot/mealie/releases/latest"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["tag_name"]


def get_latest_version() -> str:
    """
    Gets the latest release version.

    Returns:
        str: The latest release version.
    """
    MAX_DAYS_OLD = 1  # reset cache after 1 day

    global _LAST_RESET

    now = datetime.datetime.now(datetime.UTC)

    if not _LAST_RESET or now - _LAST_RESET > datetime.timedelta(days=MAX_DAYS_OLD):
        _LAST_RESET = now
        get_latest_github_release.cache_clear()

    try:
        return get_latest_github_release()
    except requests.RequestException:
        return "error fetching version"
    except KeyError:
        return "error parsing response"
    except Exception:
        return "unknown error"
