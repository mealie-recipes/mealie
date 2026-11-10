from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from .json_provider import JsonProvider


@dataclass
class ProviderFactory:
    directory: Path
    fallback_locale: str = "en-US"
    filename_format = "{locale}.{format}"

    _store: dict[str, JsonProvider] = field(default_factory=dict)

    @cached_property
    def supported_locales(self) -> list[str]:
        return [path.stem for path in self.directory.glob(self.filename_format.format(locale="*", format="json"))]

    def _load(self, locale: str) -> JsonProvider:
        filename = self.filename_format.format(locale=locale, format="json")
        return JsonProvider(self.directory / filename)

    def get(self, locale: str) -> JsonProvider:
        # locale usually comes straight from the Accept-Language header, so it must never
        # reach the filesystem or the cache key unless it names a bundled translation file
        if locale not in self.supported_locales:
            locale = self.fallback_locale

        if locale not in self._store:
            self._store[locale] = self._load(locale)

        return self._store[locale]
