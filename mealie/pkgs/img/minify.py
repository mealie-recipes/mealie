from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import Logger
from pathlib import Path

from PIL import Image

WEBP = ".webp"
FORMAT = "WEBP"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_format(image: Path) -> str:
    img = Image.open(image)
    return img.format


def sizeof_fmt(file_path: Path, decimal_places=2):
    if not file_path.exists():
        return "(File Not Found)"
    size: int | float = file_path.stat().st_size
    for unit in ["B", "kB", "MB", "GB", "TB", "PB"]:
        if size < 1024 or unit == "PiB":
            break
        size /= 1024
    return f"{size:.{decimal_places}f} {unit}"


@dataclass
class MinifierOptions:
    original: bool = True
    miniature: bool = True
    tiny: bool = True


class ABCMinifier(ABC):
    def __init__(self, purge=False, opts: MinifierOptions = None, logger: Logger = None):
        self._purge = purge
        self._opts = opts or MinifierOptions()
        self._logger = logger or Logger("Minifier")

    def get_image_sizes(self, org_img: Path, min_img: Path, tiny_img: Path):
        self._logger.info(
            f"{org_img.name} Minified: {sizeof_fmt(org_img)} -> {sizeof_fmt(min_img)} -> {sizeof_fmt(tiny_img)}"
        )

    @abstractmethod
    def minify(self, image: Path, force=True):
        ...

    def purge(self, image: Path):
        if not self._purge:
            return

        for file in image.parent.glob("*.*"):
            if file.suffix != WEBP:
                file.unlink()


class PillowMinifier(ABCMinifier):
    @staticmethod
    def to_webp(image_file: Path, dest: Path = None, quality: int = 100) -> Path:
        """
        Converts an image to the webp format in-place. The original image is not
        removed By default, the quality is set to 100.
        """
        img = Image.open(image_file)

        dest = dest or image_file.with_suffix(WEBP)
        img.save(dest, FORMAT, quality=quality)

        return dest

    @staticmethod
    def crop_center(pil_img: Image, crop_width=300, crop_height=300):
        img_width, img_height = pil_img.size
        return pil_img.crop(
            (
                (img_width - crop_width) // 2,
                (img_height - crop_height) // 2,
                (img_width + crop_width) // 2,
                (img_height + crop_height) // 2,
            )
        )

    def minify(self, image_file: Path, force=True):
        if not image_file.exists():
            raise FileNotFoundError(f"{image_file.name} does not exist")

        org_dest = image_file.parent.joinpath("original.webp")
        min_dest = image_file.parent.joinpath("min-original.webp")
        tiny_dest = image_file.parent.joinpath("tiny-original.webp")

        if not force and min_dest.exists() and tiny_dest.exists() and org_dest.exists():
            self._logger.info(f"{image_file.name} already minified")
            return

        success = False

        if self._opts.original:
            if not force and org_dest.exists():
                self._logger.info(f"{image_file.name} already minified")
            else:
                PillowMinifier.to_webp(image_file, org_dest, quality=70)
                success = True

        if self._opts.miniature:
            if not force and min_dest.exists():
                self._logger.info(f"{image_file.name} already minified")
            else:
                PillowMinifier.to_webp(image_file, min_dest, quality=70)
                self._logger.info(f"{image_file.name} minified")
                success = True

        if self._opts.tiny:
            if not force and tiny_dest.exists():
                self._logger.info(f"{image_file.name} already minified")
            else:
                img = Image.open(image_file)
                tiny_image = PillowMinifier.crop_center(img)
                tiny_image.save(tiny_dest, FORMAT, quality=70)
                self._logger.info("Tiny image saved")
                success = True

        if self._purge and success:
            self.purge(image_file)
