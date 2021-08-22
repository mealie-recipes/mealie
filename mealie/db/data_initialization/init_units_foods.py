from mealie.schema.recipe.recipe import IngredientUnit
from sqlalchemy.orm.session import Session

from ..data_access_layer import DatabaseAccessLayer


def get_default_units():
    return [
        # Volume
        IngredientUnit(name="teaspoon", abbreviation="tsp"),
        IngredientUnit(name="tablespoon", abbreviation="tbsp"),
        IngredientUnit(name="fluid ounce", abbreviation="fl oz"),
        IngredientUnit(name="cup", abbreviation="cup"),
        IngredientUnit(name="pint", abbreviation="pt"),
        IngredientUnit(name="quart", abbreviation="qt"),
        IngredientUnit(name="gallon", abbreviation="gal"),
        IngredientUnit(name="milliliter", abbreviation="ml"),
        IngredientUnit(name="liter", abbreviation="l"),
        # Mass Weight
        IngredientUnit(name="pound", abbreviation="lb"),
        IngredientUnit(name="ounce", abbreviation="oz"),
        IngredientUnit(name="gram", abbreviation="g"),
        IngredientUnit(name="kilogram", abbreviation="kg"),
        IngredientUnit(name="milligram", abbreviation="mg"),
    ]


def default_recipe_unit_init(db: DatabaseAccessLayer, session: Session) -> None:
    for unit in get_default_units():
        try:
            db.ingredient_units.create(session, unit)
            print("Ingredient Unit Committed")
        except Exception as e:
            print(e)
