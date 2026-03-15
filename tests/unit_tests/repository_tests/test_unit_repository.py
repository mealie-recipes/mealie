from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from mealie.repos.all_repositories import AllRepositories, get_repositories
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient, SaveIngredientUnit
from mealie.schema.user.user import GroupBase
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


@pytest.fixture()
def unique_local_group_id(unfiltered_database: AllRepositories) -> str:
    return str(unfiltered_database.groups.create(GroupBase(name=random_string())).id)


@pytest.fixture()
def unique_db(session: Session, unique_local_group_id: str) -> AllRepositories:
    return get_repositories(session, group_id=unique_local_group_id)


def test_unit_merger(unique_user: TestUser):
    database = unique_user.repos
    recipe: Recipe | None = None
    slug1 = random_string(10)

    unit_1 = database.ingredient_units.create(
        SaveIngredientUnit(
            name=random_string(10),
            group_id=unique_user.group_id,
        )
    )

    unit_2 = database.ingredient_units.create(
        SaveIngredientUnit(
            name=random_string(10),
            group_id=unique_user.group_id,
        )
    )

    recipe = database.recipes.create(
        Recipe(
            name=slug1,
            user_id=unique_user.user_id,
            group_id=UUID(unique_user.group_id),
            recipe_ingredient=[
                RecipeIngredient(note="", unit=unit_1),  # type: ignore
                RecipeIngredient(note="", unit=unit_2),  # type: ignore
            ],
        )  # type: ignore
    )

    # Santiy check make sure recipe got created

    assert recipe.id is not None

    for ing in recipe.recipe_ingredient:
        assert ing.unit.id in [unit_1.id, unit_2.id]  # type: ignore

    database.ingredient_units.merge(unit_2.id, unit_1.id)

    recipe = database.recipes.get_one(recipe.slug)
    assert recipe

    for ingredient in recipe.recipe_ingredient:
        assert ingredient.unit.id == unit_1.id  # type: ignore


@pytest.mark.parametrize("standard_field", ["name", "plural_name", "abbreviation", "plural_abbreviation"])
@pytest.mark.parametrize("use_bulk", [True, False])
def test_auto_inject_standardization(unique_db: AllRepositories, standard_field: str, use_bulk: bool):
    unit_in = SaveIngredientUnit(name=random_string(), group_id=unique_db.group_id).model_dump()
    unit_in[standard_field] = "gallon"

    if use_bulk:
        out_many = unique_db.ingredient_units.create_many([unit_in])
        assert len(out_many) == 1
        unit_out = out_many[0]
    else:
        unit_out = unique_db.ingredient_units.create(unit_in)

    assert unit_out.standard_unit == "cup"
    assert unit_out.standard_quantity == 16


def test_dont_auto_inject_random(unique_db: AllRepositories):
    unit_in = SaveIngredientUnit(name=random_string(), group_id=unique_db.group_id)
    unit_out = unique_db.ingredient_units.create(unit_in)

    assert unit_out.standard_quantity is None
    assert unit_out.standard_unit is None


def test_auto_inject_other_language(unique_db: AllRepositories):
    # Inject custom unit map
    GALLON = random_string()
    unique_db.ingredient_units._standardized_unit_map = {GALLON: "gallon"}

    # Create unit with translated value
    unit_in = SaveIngredientUnit(name=GALLON, group_id=unique_db.group_id)
    unit_out = unique_db.ingredient_units.create(unit_in)

    assert unit_out.standard_unit == "cup"
    assert unit_out.standard_quantity == 16


@pytest.mark.parametrize("name", ["custom-mealie-unit", "gallon"])
def test_user_standardization(unique_db: AllRepositories, name: str):
    unit_in = SaveIngredientUnit(
        name=name,
        group_id=unique_db.group_id,
        standard_quantity=random_int(1, 10),
        standard_unit=random_string(),
    )
    unit_out = unique_db.ingredient_units.create(unit_in)

    assert unit_out.standard_quantity == unit_in.standard_quantity
    assert unit_out.standard_unit == unit_in.standard_unit


def test_ignore_incomplete_standardization(unique_db: AllRepositories):
    unit_in = SaveIngredientUnit(
        name=random_string(),
        group_id=unique_db.group_id,
        standard_quantity=random_int(1, 10),
        standard_unit=None,
    )
    unit_out = unique_db.ingredient_units.create(unit_in)

    assert unit_out.standard_quantity is None
    assert unit_out.standard_unit is None

    unit_in = SaveIngredientUnit(
        name=random_string(),
        group_id=unique_db.group_id,
        standard_quantity=None,
        standard_unit=random_string(),
    )
    unit_out = unique_db.ingredient_units.create(unit_in)

    assert unit_out.standard_quantity is None
    assert unit_out.standard_unit is None
