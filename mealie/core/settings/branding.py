from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ALLOWED_IMAGE_SUFFIXES = {".svg", ".png", ".ico", ".webp", ".jpg", ".jpeg"}


class Branding(BaseSettings):
    name: str = "Mealie"
    logo_path: str | None = None
    model_config = SettingsConfigDict(env_prefix="branding_", extra="allow")

    @property
    def logo_file(self) -> Path | None:
        if not self.logo_path:
            return None

        file_path = Path(self.logo_path)
        if not file_path.is_file():
            return None

        if file_path.suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
            return None

        return file_path
