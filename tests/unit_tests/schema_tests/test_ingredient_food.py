from uuid import uuid4

from mealie.schema.recipe.recipe_ingredient import IngredientFood, IngredientUnit


class _Row:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _food_row(description):
    return _Row(
        id=uuid4(),
        name="Flour",
        plural_name=None,
        description=description,
        extras=None,
        label_id=None,
        aliases=[],
        households_with_ingredient_food=[],
        label=None,
        created_at=None,
        updated_at=None,
    )


def _unit_row(description):
    return _Row(
        id=uuid4(),
        name="Gram",
        plural_name=None,
        description=description,
        extras=None,
        fraction=True,
        abbreviation="g",
        plural_abbreviation="",
        use_abbreviation=False,
        aliases=[],
        created_at=None,
        updated_at=None,
    )


def test_food_with_null_description_validates():
    food = IngredientFood.model_validate(_food_row(None))
    assert food.description == ""


def test_food_preserves_non_null_description():
    food = IngredientFood.model_validate(_food_row("all purpose"))
    assert food.description == "all purpose"


def test_unit_with_null_description_validates():
    unit = IngredientUnit.model_validate(_unit_row(None))
    assert unit.description == ""
