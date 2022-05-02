import json

from mealie.core import root_logger
from mealie.repos.repository_factory import AllRepositories
from mealie.repos.seed.resources import foods as food_resources


def fix_slug_food_names(db: AllRepositories):
    check_for_food = "dairy-products-and-dairy-substitutes"

    food = db.ingredient_foods.get_one(check_for_food, "name")

    logger = root_logger.get_logger("init_db")

    if not food:
        logger.info(f"No food found with slug: '{check_for_food}' skipping fix")
        return

    all_foods = db.ingredient_foods.get_all()

    seed_foods: dict[str, str] = json.loads(food_resources.en_US.read_text())

    for food in all_foods:
        if food.name in seed_foods:
            food.name = seed_foods[food.name]
            logger.info(f"Updating food: {food.name}")
            db.ingredient_foods.update(food.id, food)
