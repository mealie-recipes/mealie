from scrape_schema_recipe import scrape_url
from slugify import slugify
from utils.logger import logger

from services.image_services import scrape_image
from services.recipe_services import Recipe


def create_from_url(url: str) -> dict:
    recipe_data = process_recipe_url(url)
    recipe = Recipe(**recipe_data)

    return recipe.save_to_db()


def process_recipe_url(url: str) -> dict:
    new_recipe: dict = scrape_url(url, python_objects=True)[0]
    logger.info(f"Recipe Scraped From Web: {new_recipe}")

    if not new_recipe:
        return "fail"  # TODO: Return Better Error Here

    slug = slugify(new_recipe["name"])
    mealie_tags = {
        "slug": slug,
        "orgURL": url,
        "categories": [],
        "tags": [],
        "dateAdded": None,
        "notes": [],
        "extras": [],
    }

    new_recipe.update(mealie_tags)

    try:
        img_path = scrape_image(new_recipe.get("image"), slug)
        new_recipe["image"] = img_path.name
    except:
        new_recipe["image"] = None

    return new_recipe
