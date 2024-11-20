from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from .json_provider import JsonProvider


@dataclass(slots=True)
class InUseProvider:
    provider: JsonProvider
    locks: int


@dataclass
class ProviderFactory:
    directory: Path
    fallback_locale: str = "en-US"
    filename_format = "{locale}.{format}"

    _store: dict[str, InUseProvider] = field(default_factory=dict)

    @property
    def fallback_file(self) -> Path:
        return self.directory / self.filename_format.format(locale=self.fallback_locale, format="json")

    @cached_property
    def supported_locales(self) -> list[str]:
        return [path.stem for path in self.directory.glob(self.filename_format.format(locale="*", format="json"))]

    def _load(self, locale: str) -> JsonProvider:
        filename = self.filename_format.format(locale=locale, format="json")
        path = self.directory / filename

        return JsonProvider(path) if path.exists() else JsonProvider(self.fallback_file)

    def release(self, locale) -> None:
        if locale in self._store:
            self._store[locale].locks -= 1
            if self._store[locale].locks == 0:
                del self._store[locale]

    def get(self, locale: str) -> JsonProvider:
        if locale in self._store:
            self._store[locale].locks += 1
        else:
            self._store[locale] = InUseProvider(provider=self._load(locale), locks=1)

        return self._store[locale].provider
