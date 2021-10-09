from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path

import i18n
from bcrypt import os

CWD = Path(__file__).parent
TRANSLATIONS = CWD / "messages"


class AbstractLocaleProvider(ABC):
    @abstractmethod
    def t(self, key):
        pass


class i18nProvider(AbstractLocaleProvider):
    def __init__(self, locale):
        i18n.set("file_format", "json")
        i18n.set("filename_format", "{locale}.{format}")
        i18n.set("skip_locale_root_data", True)
        i18n.load_path.append(TRANSLATIONS)
        i18n.set("locale", locale)
        i18n.set("fallback", "en-US")
        self._t = i18n.t

    def t(self, key):
        return self._t(key)


@lru_cache()
def get_locale_provider():
    lang = os.environ.get("LANG", "en-US")
    return i18nProvider(lang)
