from pathlib import Path

from PIL import Image

from mealie.pkgs.img.minify import PillowMinifier
from tests import data as test_data


def _make_large_image(dest: Path, size: tuple[int, int] = (4000, 3000)) -> Path:
    """Create a JPEG larger than the default 2048px bound for resize testing."""
    img = Image.new("RGB", size)
    pixels = img.load()
    # A mildly textured (photographic-ish) image so it does not compress to nothing.
    for y in range(0, size[1], 2):
        for x in range(0, size[0], 2):
            pixels[x, y] = ((x * 7) % 256, (y * 5 + x) % 256, ((x + y) * 3) % 256)
    img.save(dest, "JPEG", quality=85)
    return dest


def test_to_jpg_defaults_do_not_resize(tmp_path: Path):
    """Backwards-compatibility: without max_dimension the image keeps its dimensions."""
    src = _make_large_image(tmp_path / "large.jpg", size=(4000, 3000))
    dest = tmp_path / "out.jpg"

    PillowMinifier.to_jpg(src, dest=dest)

    with Image.open(dest) as result:
        assert result.size == (4000, 3000)


def test_to_jpg_max_dimension_downscales(tmp_path: Path):
    """max_dimension bounds the longest side while preserving aspect ratio."""
    src = _make_large_image(tmp_path / "large.jpg", size=(4000, 3000))
    dest = tmp_path / "out.jpg"

    PillowMinifier.to_jpg(src, dest=dest, quality=80, max_dimension=2048)

    with Image.open(dest) as result:
        assert max(result.size) <= 2048
        # Aspect ratio preserved (4:3 -> 2048x1536).
        assert result.size == (2048, 1536)


def test_to_jpg_max_dimension_never_upscales(tmp_path: Path):
    """Images already within the bound are left at their original size."""
    src = _make_large_image(tmp_path / "small.jpg", size=(800, 600))
    dest = tmp_path / "out.jpg"

    PillowMinifier.to_jpg(src, dest=dest, max_dimension=2048)

    with Image.open(dest) as result:
        assert result.size == (800, 600)


def test_to_jpg_max_dimension_shrinks_encoded_size(tmp_path: Path):
    """Resizing + moderate quality yields a smaller payload than the q100/no-resize default.

    This is the regression the AI-image-import path depends on: a full-resolution
    photo must not be inflated past a provider's image-size limit.
    """
    src = _make_large_image(tmp_path / "photo.jpg", size=(4032, 3024))

    inflated = tmp_path / "inflated.jpg"
    PillowMinifier.to_jpg(src, dest=inflated)  # old behavior: quality=100, no resize

    minified = tmp_path / "minified.jpg"
    PillowMinifier.to_jpg(src, dest=minified, quality=80, max_dimension=2048)

    assert minified.stat().st_size < inflated.stat().st_size


def test_to_jpg_repo_fixture_resizes(tmp_path: Path):
    """Sanity check against the repo's real JPEG fixture."""
    dest = tmp_path / "fixture-out.jpg"

    PillowMinifier.to_jpg(test_data.images_test_image_1, dest=dest, max_dimension=64)

    with Image.open(dest) as result:
        assert max(result.size) <= 64
