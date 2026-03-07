import pytest
from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFoodAlias,
    CreateIngredientUnitAlias,
    IngredientFood,
    IngredientUnit,
    SaveIngredientFood,
    SaveIngredientUnit,
)
from mealie.schema.user.user import GroupBase
from tests.utils.factories import random_int, random_string


@pytest.fixture()
def unique_local_group_id(unfiltered_database: AllRepositories) -> UUID4:
    return str(unfiltered_database.groups.create(GroupBase(name=random_string())).id)


@pytest.fixture()
def unique_db(session: Session, unique_local_group_id: str):
    return get_repositories(session, group_id=unique_local_group_id)


@pytest.fixture()
def parsed_ingredient_data(
    unique_db: AllRepositories, unique_local_group_id: UUID4
) -> tuple[list[IngredientFood], list[IngredientUnit]]:
    foods = unique_db.ingredient_foods.create_many(
        [
            SaveIngredientFood(name="potatoes", group_id=unique_local_group_id),
            SaveIngredientFood(name="onion", group_id=unique_local_group_id),
            SaveIngredientFood(name="green onion", group_id=unique_local_group_id),
            SaveIngredientFood(name="frozen pearl onions", group_id=unique_local_group_id),
            SaveIngredientFood(name="bell peppers", group_id=unique_local_group_id),
            SaveIngredientFood(name="red pepper flakes", group_id=unique_local_group_id),
            SaveIngredientFood(name="fresh ginger", group_id=unique_local_group_id),
            SaveIngredientFood(name="ground ginger", group_id=unique_local_group_id),
            SaveIngredientFood(name="ñör̃m̈ãl̈ĩz̈ẽm̈ẽ", group_id=unique_local_group_id),
            SaveIngredientFood(name="PluralFoodTest", plural_name="myfoodisplural", group_id=unique_local_group_id),
            SaveIngredientFood(
                name="IHaveAnAlias",
                group_id=unique_local_group_id,
                aliases=[CreateIngredientFoodAlias(name="thisismyalias")],
            ),
        ]
    )

    foods.extend(
        unique_db.ingredient_foods.create_many(
            [
                SaveIngredientFood(name=f"{random_string()} food", group_id=unique_local_group_id)
                for _ in range(random_int(10, 15))
            ]
        )
    )

    units = unique_db.ingredient_units.create_many(
        [
            SaveIngredientUnit(name="Cups", group_id=unique_local_group_id),
            SaveIngredientUnit(name="Tablespoon", group_id=unique_local_group_id),
            SaveIngredientUnit(name="Teaspoon", group_id=unique_local_group_id),
            SaveIngredientUnit(name="Stalk", group_id=unique_local_group_id),
            SaveIngredientUnit(name="My Very Long Unit Name", abbreviation="mvlun", group_id=unique_local_group_id),
            SaveIngredientUnit(
                name="PluralUnitName",
                plural_name="abc123",
                abbreviation="doremiabc",
                plural_abbreviation="doremi123",
                group_id=unique_local_group_id,
            ),
            SaveIngredientUnit(
                name="IHaveAnAliasToo",
                group_id=unique_local_group_id,
                aliases=[CreateIngredientUnitAlias(name="thisismyalias")],
            ),
        ]
    )

    units.extend(
        unique_db.ingredient_foods.create_many(
            [
                SaveIngredientUnit(name=f"{random_string()} unit", group_id=unique_local_group_id)
                for _ in range(random_int(10, 15))
            ]
        )
    )

    return foods, units
