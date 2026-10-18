import hashlib
import shutil
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageOps

from mealie.core.root_logger import get_logger
from mealie.services._base_service import BaseService

# Checked in this order; the first one found in DATA_DIR/branding is used
LOGO_FILENAMES = ["logo.png", "logo.webp", "logo.jpg", "logo.jpeg"]

FAVICON_SIZES = [16, 32, 48, 64]


@dataclass(frozen=True)
class IconSpec:
    size: int
    background: str | None = None
    """Fill colour behind the logo; None keeps it transparent"""
    scale: float = 1.0
    """Share of the canvas the logo may take up"""


ICON_SPECS: dict[str, IconSpec] = {
    "logo.png": IconSpec(256),
    "favicon-32x32.png": IconSpec(32),
    "android-chrome-192x192.png": IconSpec(192),
    "android-chrome-512x512.png": IconSpec(512),
    # Android crops maskable icons to a shape inside the middle 80% of the canvas
    "android-chrome-maskable-192x192.png": IconSpec(192, "#FFFFFF", 0.6),
    "android-chrome-maskable-512x512.png": IconSpec(512, "#FFFFFF", 0.6),
    # iOS fills transparency with black on the home screen
    "apple-touch-icon.png": IconSpec(180, "#FFFFFF", 0.8),
}

BRANDING_FILES = [*ICON_SPECS, "favicon.ico"]


@dataclass(frozen=True)
class Branding:
    version: str
    """Changes whenever the logo does, so clients can cache icons by it"""
    directory: Path

    def get_file(self, filename: str) -> Path | None:
        if filename not in BRANDING_FILES:
            return None
        return self.directory / filename


class BrandingService(BaseService):
    """Builds the app's icons from a logo the admin drops into DATA_DIR/branding"""

    def __init__(self) -> None:
        super().__init__()
        self.branding_dir = self.directories.DATA_DIR / "branding"
        self.generated_dir = self.branding_dir / ".generated"

    def find_logo(self) -> Path | None:
        for filename in LOGO_FILENAMES:
            path = self.branding_dir / filename
            if path.is_file():
                return path
        return None

    def load(self) -> Branding | None:
        logo = self.find_logo()
        if logo is None:
            return None

        version = hashlib.sha256(logo.read_bytes()).hexdigest()[:12]
        out_dir = self.generated_dir / version
        complete_marker = out_dir / ".complete"

        if not complete_marker.exists():
            self.logger.info(f"generating icons from custom logo {logo}")
            shutil.rmtree(self.generated_dir, ignore_errors=True)
            out_dir.mkdir(parents=True)
            self.generate_icons(logo, out_dir)
            complete_marker.touch()

        return Branding(version=version, directory=out_dir)

    @staticmethod
    def generate_icons(logo: Path, out_dir: Path) -> None:
        with Image.open(logo) as img:
            source = ImageOps.exif_transpose(img).convert("RGBA")

        for filename, spec in ICON_SPECS.items():
            BrandingService._render(source, spec).save(out_dir / filename, format="PNG", optimize=True)

        favicon = BrandingService._render(source, IconSpec(max(FAVICON_SIZES)))
        favicon.save(out_dir / "favicon.ico", format="ICO", sizes=[(s, s) for s in FAVICON_SIZES])

    @staticmethod
    def _render(source: Image.Image, spec: IconSpec) -> Image.Image:
        canvas = Image.new("RGBA", (spec.size, spec.size), spec.background or (0, 0, 0, 0))

        logo_size = max(1, round(spec.size * spec.scale))
        logo = ImageOps.contain(source, (logo_size, logo_size), Image.Resampling.LANCZOS)

        offset = ((spec.size - logo.width) // 2, (spec.size - logo.height) // 2)
        canvas.alpha_composite(logo, offset)
        return canvas


@lru_cache(maxsize=1)
def get_branding() -> Branding | None:
    """The custom logo, if one is set. Read once, so a new logo needs a restart."""
    try:
        return BrandingService().load()
    except Exception:
        get_logger().exception("could not load the custom logo, using the default one")
        return None
