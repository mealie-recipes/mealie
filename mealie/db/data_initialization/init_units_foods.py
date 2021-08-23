from mealie.schema.recipe.units_and_foods import CreateIngredientUnit
from sqlalchemy.orm.session import Session

from ..data_access_layer import DatabaseAccessLayer


def get_default_units():
    return [
        # Volume
        CreateIngredientUnit(name="teaspoon", abbreviation="tsp"),
        CreateIngredientUnit(name="tablespoon", abbreviation="tbsp"),
        CreateIngredientUnit(name="fluid ounce", abbreviation="fl oz"),
        CreateIngredientUnit(name="cup", abbreviation="cup"),
        CreateIngredientUnit(name="pint", abbreviation="pt"),
        CreateIngredientUnit(name="quart", abbreviation="qt"),
        CreateIngredientUnit(name="gallon", abbreviation="gal"),
        CreateIngredientUnit(name="milliliter", abbreviation="ml"),
        CreateIngredientUnit(name="liter", abbreviation="l"),
        # Mass Weight
        CreateIngredientUnit(name="pound", abbreviation="lb"),
        CreateIngredientUnit(name="ounce", abbreviation="oz"),
        CreateIngredientUnit(name="gram", abbreviation="g"),
        CreateIngredientUnit(name="kilogram", abbreviation="kg"),
        CreateIngredientUnit(name="milligram", abbreviation="mg"),
    ]


def default_recipe_unit_init(db: DatabaseAccessLayer, session: Session) -> None:
    for unit in get_default_units():
        try:
            db.ingredient_units.create(session, unit)
            print("Ingredient Unit Committed")
        except Exception as e:
            print(e)
