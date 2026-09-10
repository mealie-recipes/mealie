from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ALLOWED_IMAGE_SUFFIXES = {".svg", ".png", ".ico", ".webp", ".jpg", ".jpeg"}


class Branding(BaseSettings):
    name: str = "Mealie"
    html_title: str = "Mealie"
    icon_path: str | None = None
    favicon_path: str | None = None
    model_config = SettingsConfigDict(env_prefix="branding_", extra="allow")

    def _resolve_file(self, path: str | None) -> Path | None:
        if not path:
            return None

        file_path = Path(path)
        if not file_path.is_file():
            return None

        if file_path.suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
            return None

        return file_path

    @property
    def icon_file(self) -> Path | None:
        return self._resolve_file(self.icon_path)

    @property
    def favicon_file(self) -> Path | None:
        return self._resolve_file(self.favicon_path)
