import shutil
from pathlib import Path

from fastapi.logger import logger
from mealie.core.config import app_dirs
from mealie.db.database import db
from mealie.db.db_setup import create_session
from PIL import Image
from sqlalchemy.orm.session import Session


def minify_image(image_file: Path, min_dest: Path, tiny_dest: Path):
    """Minifies an image in it's original file format. Quality is lost

    Args:
        my_path (Path): Source Files
        min_dest (Path): FULL Destination File Path
        tiny_dest (Path): FULL Destination File Path
    """
    try:
        img = Image.open(image_file)
        basewidth = 720
        wpercent = basewidth / float(img.size[0])
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        img.save(min_dest, quality=70)

        tiny_image = crop_center(img)
        tiny_image.save(tiny_dest, quality=70)

    except Exception:
        shutil.copy(image_file, min_dest)
        shutil.copy(image_file, tiny_dest)


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


def sizeof_fmt(size, decimal_places=2):
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


def validate_slugs_in_database(session: Session = None):
    def check_image_path(image_name: str, slug_path: str) -> bool:
        existing_path: Path = app_dirs.IMG_DIR.joinpath(image_name)
        slug_path: Path = app_dirs.IMG_DIR.joinpath(slug_path)

        if existing_path.is_dir():
            slug_path.rename(existing_path)
        else:
            logger.info("No Image Found")

    session = session or create_session()
    all_recipes = db.recipes.get_all(session)

    slugs_and_images = [(x.slug, x.image) for x in all_recipes]

    for slug, image in slugs_and_images:
        image_slug = image.split(".")[0]  # Remove Extension
        if slug != image_slug:
            logger.info(f"{slug}, Doesn't Match '{image_slug}'")
            check_image_path(image, slug)


def migrate_images():
    print("Checking for Images to Minify...")

    move_all_images()

    # Minify Loop
    for image in app_dirs.IMG_DIR.glob("*/original.*"):
        min_dest = image.parent.joinpath(f"min-original{image.suffix}")
        tiny_dest = image.parent.joinpath(f"tiny-original{image.suffix}")

        if min_dest.exists() and tiny_dest.exists():
            continue

        minify_image(image, min_dest, tiny_dest)

        org_size = sizeof_fmt(image.stat().st_size)
        dest_size = sizeof_fmt(min_dest.stat().st_size)
        tiny_size = sizeof_fmt(tiny_dest.stat().st_size)
        logger.info(f"{image.name} Minified: {org_size} -> {dest_size} -> {tiny_size}")

    logger.info("Finished Minification Check")


if __name__ == "__main__":
    migrate_images()
    validate_slugs_in_database()
