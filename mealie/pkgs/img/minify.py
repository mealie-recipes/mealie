from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import Logger
from pathlib import Path

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()


@dataclass
class ImageFormat:
    suffix: str
    format: str
    modes: list[str]
    """If the image is not in the correct mode, it will be converted to the first mode in the list"""


JPG = ImageFormat(".jpg", "JPEG", ["RGB"])
WEBP = ImageFormat(".webp", "WEBP", ["RGB", "RGBA"])
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".avif"}


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
    uncropped: bool = True


class ABCMinifier(ABC):
    def __init__(self, purge=False, opts: MinifierOptions | None = None, logger: Logger | None = None):
        self._purge = purge
        self._opts = opts or MinifierOptions()
        self._logger = logger or Logger("Minifier")

    def get_image_sizes(self, org_img: Path, min_img: Path, tiny_img: Path):
        self._logger.info(
            f"{org_img.name} Minified: {sizeof_fmt(org_img)} -> {sizeof_fmt(min_img)} -> {sizeof_fmt(tiny_img)}"
        )

    @abstractmethod
    def minify(self, image_path: Path, force=True): ...

    def purge(self, image: Path):
        if not self._purge:
            return

        for file in image.parent.glob("*.*"):
            if file.suffix != WEBP.suffix:
                file.unlink()


class PillowMinifier(ABCMinifier):
    @staticmethod
    def _convert_image(
        image_file: Path | None = None, image_format: ImageFormat, dest: Path | None = None, quality: int = 100, img: Image.Image | None = None
    ) -> Path:
        """
        Converts an image to the specified format in-place. The original image is not
        removed. By default, the quality is set to 100.
        """
        if img is None:
            if image_file is None:
                raise ValueError("Must provide either image_file or img.")
            img = Image.open(image_file)

        if img.mode not in image_format.modes:
            img = img.convert(image_format.modes[0])
        
        img = ImageOps.exif_transpose(img)

        if dest is None:
            if image_file is None:
                raise ValueError("If dest is not provided, image_file must be.")
            dest = image_file.with_suffix(image_format.suffix)
        
        img.save(dest, image_format.format, quality=quality)

        return dest

    @staticmethod
    def to_jpg(image_file_path: Path | None = None, dest_path: Path | None = None, quality: int = 100, img: Image.Image | None = None) -> Path:
        return PillowMinifier._convert_image(image_file_path, JPG, dest_path, quality, img)

    @staticmethod
    def to_webp(image_file_path: Path | None = None, dest_path: Path | None = None, quality: int = 100, img: Image.Image | None = None) -> Path:
        return PillowMinifier._convert_image(image_file_path, WEBP, dest_path, quality, img)

    @staticmethod
    def crop_center_square(pil_img: Image, size: int = 300):
        width, height = pil_img.size
        crop_size = min(width, height)

        left = (width - crop_size) // 2
        top = (height - crop_size) // 2
        right = left + crop_size
        bottom = top + crop_size

        return pil_img.crop((left, top, right, bottom)).resize((size, size), Image.LANCZOS)

        # For retina displays, double the target size
        if high_res:
            target_width *= 2
            target_height *= 2

        org_dest = image_file.parent.joinpath("original.webp")
        min_dest = image_file.parent.joinpath("min-original.webp")
        tiny_dest = image_file.parent.joinpath("tiny-original.webp")
        uncropped_dest = image_file.parent.joinpath("uncropped-original.webp")

        if not force and min_dest.exists() and tiny_dest.exists() and org_dest.exists() and uncropped_dest.exists():
            self._logger.info(f"{image_file.name} already exists in all formats")
            return

        success = False

        try:
            with Image.open(image_file) as img:

                if self._opts.uncropped:
                    if not force and uncropped_dest.exists():
                        self._logger.info(f"{uncropped_dest} already exists")
                    else:
                        result_path = PillowMinifier.to_webp(dest_path=uncropped_dest, quality=100, img=img.copy())
                        self._logger.info(f"{result_path} created")
                        success = True

                if self._opts.original:
                    if not force and org_dest.exists():
                        self._logger.info(f"{org_dest} already exists")
                    else:
                        result_path = PillowMinifier.to_webp(dest_path=org_dest, quality=80, img=img.copy())
                        self._logger.info(f"{result_path} created")
                        success = True

                if self._opts.miniature:
                    if not force and min_dest.exists():
                        self._logger.info(f"{min_dest} already exists")
                    else:
                        mini = img.copy()
                        mini.thumbnail((1024, 1024), Image.LANCZOS)
                        result_path = PillowMinifier.to_webp(dest_path=min_dest, quality=80, img=mini)
                        self._logger.info(f"{result_path} created")
                        success = True

                if self._opts.tiny:
                    if not force and tiny_dest.exists():
                        self._logger.info(f"{tiny_dest} already exists")
                    else:
                        tiny = PillowMinifier.crop_center_square(img.copy(), size=300)
                        result_path = PillowMinifier.to_webp(dest_path=tiny_dest, quality=80, img=tiny)
                        self._logger.info(f"{result_path} created")
                        success = True

        except Exception as e:
            self._logger.error(f"[ERROR] Failed to minify {image_file.name}. Error: {e}")
            raise

        if self._purge and success:
            self.purge(image_path)
