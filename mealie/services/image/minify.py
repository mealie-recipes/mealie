import shutil
from dataclasses import dataclass
from pathlib import Path

from mealie.core import root_logger
from mealie.core.config import app_dirs
from mealie.schema.recipe import Recipe
from PIL import Image

logger = root_logger.get_logger()


@dataclass
class ImageSizes:
    org: str
    min: str
    tiny: str


def get_image_sizes(org_img: Path, min_img: Path, tiny_img: Path) -> ImageSizes:
    return ImageSizes(org=sizeof_fmt(org_img), min=sizeof_fmt(min_img), tiny=sizeof_fmt(tiny_img))


def minify_image(image_file: Path) -> ImageSizes:
    """Minifies an image in it's original file format. Quality is lost

    Args:
        my_path (Path): Source Files
        min_dest (Path): FULL Destination File Path
        tiny_dest (Path): FULL Destination File Path
    """

    def cleanup(dir: Path) -> None:
        for file in dir.glob("*.*"):
            if file.suffix != ".webp":
                file.unlink()

    org_dest = image_file.parent.joinpath("original.webp")
    min_dest = image_file.parent.joinpath("min-original.webp")
    tiny_dest = image_file.parent.joinpath("tiny-original.webp")

    if min_dest.exists() and tiny_dest.exists() and org_dest.exists():
        return
    try:
        img = Image.open(image_file)

        img.save(org_dest, "WEBP")
        basewidth = 720
        wpercent = basewidth / float(img.size[0])
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        img.save(min_dest, "WEBP", quality=70)

        tiny_image = crop_center(img)
        tiny_image.save(tiny_dest, "WEBP", quality=70)

        cleanup_images = True

    except Exception:
        shutil.copy(image_file, min_dest)
        shutil.copy(image_file, tiny_dest)

    image_sizes = get_image_sizes(image_file, min_dest, tiny_dest)

    logger.info(f"{image_file.name} Minified: {image_sizes.org} -> {image_sizes.min} -> {image_sizes.tiny}")

    if cleanup_images:
        cleanup(image_file.parent)

    return image_sizes


def crop_center(pil_img, crop_width=300, crop_height=300):
    img_width, img_height = pil_img.size
    return pil_img.crop(
        (
            (img_width - crop_width) // 2,
            (img_height - crop_height) // 2,
            (img_width + crop_width) // 2,
            (img_height + crop_height) // 2,
        )
    )


def sizeof_fmt(file_path: Path, decimal_places=2):
    if not file_path.exists():
        return "(File Not Found)"
    size = file_path.stat().st_size
    for unit in ["B", "kB", "MB", "GB", "TB", "PB"]:
        if size < 1024.0 or unit == "PiB":
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


def move_all_images():
    for image_file in app_dirs.IMG_DIR.iterdir():
        if image_file.is_file():
            if image_file.name == ".DS_Store":
                continue
            new_folder = app_dirs.IMG_DIR.joinpath(image_file.stem)
            new_folder.mkdir(parents=True, exist_ok=True)
            new_file = new_folder.joinpath(f"original{image_file.suffix}")
            if new_file.is_file():
                new_file.unlink()
            image_file.rename(new_file)
        if image_file.is_dir():
            slug = image_file.name
            image_file.rename(Recipe(slug=slug).image_dir)


def migrate_images():
    logger.info("Checking for Images to Minify...")

    move_all_images()

    for image in app_dirs.RECIPE_DATA_DIR.glob("**/original.*"):

        minify_image(image)

    logger.info("Finished Minification Check")


if __name__ == "__main__":
    migrate_images()
