from __future__ import annotations

_USER_AGENTS_MANAGER: UserAgentsManager | None = None


def get_user_agents_manager() -> UserAgentsManager:
    global _USER_AGENTS_MANAGER

    if not _USER_AGENTS_MANAGER:
        _USER_AGENTS_MANAGER = UserAgentsManager()

    return _USER_AGENTS_MANAGER


class UserAgentsManager:
    def __init__(self) -> None:
        self._user_agents: list[str] | None = None

    @property
    def user_agents(self) -> list[str]:
        if not self._user_agents:
            self._user_agents = self._fetch_user_agents()

        return self._user_agents

    def _fetch_user_agents(self) -> list[str]:
        user_agents: list[str] = []

        try:
            from recipe_scrapers._abstract import HEADERS

            user_agents.append(HEADERS["User-Agent"])
        except (ImportError, KeyError):
            user_agents.append("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/128.0")

        with open("user_agents.txt") as f:
            for line in f:
                user_agents.append(line.strip())

        return user_agents
