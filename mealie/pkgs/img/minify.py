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


class ABCMinifier(ABC):
    def __init__(self, purge=False, opts: MinifierOptions | None = None, logger: Logger | None = None):
        self._purge = purge
        self._opts = opts or MinifierOptions()
        self.logger = logger or Logger("Minifier")

    def get_image_sizes(self, org_img: Path, min_img: Path, tiny_img: Path):
        self.logger.info(
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
        image_file: Path | None = None,
        image_format: ImageFormat = WEBP,
        dest: Path | None = None,
        quality: int = 100,
        img: Image.Image | None = None,
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
    def to_jpg(
        image_file_path: Path | None = None,
        dest: Path | None = None,
        quality: int = 100,
        img: Image.Image | None = None,
    ) -> Path:
        return PillowMinifier._convert_image(
            image_file=image_file_path, image_format=JPG, dest=dest, quality=quality, img=img
        )

    @staticmethod
    def to_webp(
        image_file_path: Path | None = None,
        dest: Path | None = None,
        quality: int = 100,
        img: Image.Image | None = None,
    ) -> Path:
        return PillowMinifier._convert_image(
            image_file=image_file_path, image_format=WEBP, dest=dest, quality=quality, img=img
        )

    @staticmethod
    def crop_center(img: Image.Image, size=(300, 300), high_res: bool = True) -> Image.Image:
        img = img.copy()
        target_width, target_height = size

        # For retina displays, double the target size
        if high_res:
            target_width *= 2
            target_height *= 2

        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        # If original image smaller than target, do not upscale
        if img.width < size[0] or img.height < size[1]:
            return img

        # Resize first to fill area while preserving aspect ratio
        if img_ratio > target_ratio:
            # Wider than target
            scale_height = target_height
            scale_width = int(scale_height * img_ratio)
        else:
            # Taller than target
            scale_width = target_width
            scale_height = int(scale_width / img_ratio)

        img = img.resize((scale_width, scale_height), Image.LANCZOS)

        # Crop center of the resized image
        left = (img.width - target_width) // 2
        top = (img.height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        return img.crop((left, top, right, bottom))

    def minify(self, image_path: Path, force=True):
        if not image_path.exists():
            raise FileNotFoundError(f"{image_path.name} does not exist")

        org_dest = image_path.parent.joinpath("original.webp")
        min_dest = image_path.parent.joinpath("min-original.webp")
        tiny_dest = image_path.parent.joinpath("tiny-original.webp")

        if not force and min_dest.exists() and tiny_dest.exists() and org_dest.exists():
            self.logger.info(f"{image_path.name} already exists in all formats")
            return

        success = False

        try:
            with Image.open(image_path) as img:
                if self._opts.original:
                    if not force and org_dest.exists():
                        self.logger.info(f"{org_dest} already exists")
                    else:
                        original = img.copy()
                        original.thumbnail((2048, 2048), Image.LANCZOS)
                        result_path = PillowMinifier.to_webp(dest=org_dest, quality=80, img=original)
                        self.logger.info(f"{result_path} created")
                        success = True

                if self._opts.miniature:
                    if not force and min_dest.exists():
                        self.logger.info(f"{min_dest} already exists")
                    else:
                        mini = img.copy()
                        mini.thumbnail((1024, 1024), Image.LANCZOS)
                        result_path = PillowMinifier.to_webp(dest=min_dest, quality=80, img=mini)
                        self.logger.info(f"{result_path} created")
                        success = True

                if self._opts.tiny:
                    if not force and tiny_dest.exists():
                        self.logger.info(f"{tiny_dest} already exists")
                    else:
                        tiny = PillowMinifier.crop_center(img.copy(), size=(300, 300))
                        result_path = PillowMinifier.to_webp(dest=tiny_dest, quality=80, img=tiny)
                        self.logger.info(f"{result_path} created")
                        success = True

        except Exception as e:
            self.logger.error(f"[ERROR] Failed to minify {image_path.name}. Error: {e}")
            raise

        if self._purge and success:
            self.purge(image_path)
