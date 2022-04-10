from abc import abstractmethod
from functools import lru_cache
from pathlib import Path
from typing import Protocol

from fastapi import Header

from mealie.pkgs import i18n

CWD = Path(__file__).parent
TRANSLATIONS = CWD / "messages"


class Translator(Protocol):
    @abstractmethod
    def t(self, key, default=None, **kwargs):
        pass


@lru_cache()
def _load_factory() -> i18n.ProviderFactory:
    return i18n.ProviderFactory(
        directory=TRANSLATIONS,
        fallback_locale="en-US",
    )


def local_provider(accept_language: str | None = Header(None)) -> Translator:
    factory = _load_factory()
    accept_language = accept_language or "en-US"
    return factory.get(accept_language)
