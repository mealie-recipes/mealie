import json
from pathlib import Path

from mealie.core.root_logger import get_logger
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe import CreateIngredientFood, CreateIngredientUnit

CWD = Path(__file__).parent
logger = get_logger(__name__)


def get_default_foods():
    with open(CWD.joinpath("resources", "foods", "en-us.json"), "r") as f:
        foods = json.loads(f.read())
    return foods


def get_default_units() -> dict[str, str]:
    with open(CWD.joinpath("resources", "units", "en-us.json"), "r") as f:
        units = json.loads(f.read())
    return units


def default_recipe_unit_init(db: AllRepositories) -> None:
    for unit in get_default_units().values():
        try:
            db.ingredient_units.create(
                CreateIngredientUnit(
                    name=unit["name"], description=unit["description"], abbreviation=unit["abbreviation"]
                )
            )
        except Exception as e:
            logger.error(e)

    for food in get_default_foods():
        try:

            db.ingredient_foods.create(CreateIngredientFood(name=food, description=""))
        except Exception as e:
            logger.error(e)
