from __future__ import annotations

import os
import random

_USER_AGENTS_MANAGER: UserAgentsManager | None = None


def get_user_agents_manager() -> UserAgentsManager:
    global _USER_AGENTS_MANAGER

    if not _USER_AGENTS_MANAGER:
        _USER_AGENTS_MANAGER = UserAgentsManager()

    return _USER_AGENTS_MANAGER


class UserAgentsManager:
    def __init__(self) -> None:
        self._user_agents: list[str] | None = None
        self._user_agents_text_path = os.path.join(os.path.dirname(__file__), "user-agents.txt")

    def get_scrape_headers(self, user_agent: str | None = None) -> dict[str, str]:
        # From: https://scrapeops.io/web-scraping-playbook/403-forbidden-error-web-scraping/#optimize-request-headers
        if user_agent is None:
            user_agent = random.choice(self.user_agents)

        return {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

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

        with open(self._user_agents_text_path) as f:
            for line in f:
                if not line:
                    continue
                user_agents.append(line.strip())

        return user_agents
