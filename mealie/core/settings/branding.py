from pathlib import Path

from pydantic import PrivateAttr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ALLOWED_IMAGE_SUFFIXES = {".svg", ".png", ".ico", ".webp", ".jpg", ".jpeg"}


class Branding(BaseSettings):
    name: str = "Mealie"
    logo_path: str | None = None
    model_config = SettingsConfigDict(env_prefix="branding_", extra="allow", validate_assignment=True)

    _logo_file: Path | None = PrivateAttr(default=None)

    @model_validator(mode="after")
    def _validate_logo_file(self) -> "Branding":
        # Resolved on construction/assignment rather than on every read, so callers (and the
        # startup warning logged in app.py's lifespan_fn) don't re-check the filesystem on every
        # /api/app/about request.
        self._logo_file = None
        if not self.logo_path:
            return self

        file_path = Path(self.logo_path)
        if file_path.is_file() and file_path.suffix.lower() in ALLOWED_IMAGE_SUFFIXES:
            self._logo_file = file_path

        return self

    @property
    def logo_file(self) -> Path | None:
        return self._logo_file
