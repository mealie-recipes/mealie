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
        # Resolved on construction/assignment rather than on every read, so the fallback warning
        # below is logged when settings actually change, not on every /api/app/about request.
        self._logo_file = None
        if not self.logo_path:
            return self

        file_path = Path(self.logo_path)
        if file_path.is_file() and file_path.suffix.lower() in ALLOWED_IMAGE_SUFFIXES:
            self._logo_file = file_path
        else:
            # Deferred import to avoid a circular import: root_logger -> config -> settings -> branding
            from mealie.core.root_logger import get_logger

            get_logger().warning(
                f'BRANDING_LOGO_PATH="{self.logo_path}" is not a readable image file '
                f"({', '.join(sorted(ALLOWED_IMAGE_SUFFIXES))}); falling back to the default logo"
            )

        return self

    @property
    def logo_file(self) -> Path | None:
        return self._logo_file
