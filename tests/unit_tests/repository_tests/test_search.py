from datetime import datetime, timezone

import pytest

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe_ingredient import IngredientUnit, SaveIngredientUnit
from mealie.schema.response.pagination import OrderDirection, PaginationQuery
from mealie.schema.user.user import GroupBase
from tests.utils.factories import random_int, random_string


@pytest.fixture()
def unique_local_group_id(database: AllRepositories) -> str:
    return str(database.groups.create(GroupBase(name=random_string())).id)


@pytest.fixture()
def search_units(database: AllRepositories, unique_local_group_id: str) -> list[IngredientUnit]:
    units = [
        SaveIngredientUnit(
            group_id=unique_local_group_id,
            name="Tea Spoon",
            abbreviation="tsp",
        ),
        SaveIngredientUnit(
            group_id=unique_local_group_id,
            name="Table Spoon",
            abbreviation="tbsp",
        ),
        SaveIngredientUnit(
            group_id=unique_local_group_id,
            name="Cup",
        ),
        SaveIngredientUnit(
            group_id=unique_local_group_id,
            name="Píñch",
        ),
        SaveIngredientUnit(
            group_id=unique_local_group_id,
            name="Unit with a very cool name",
        ),
        SaveIngredientUnit(
            group_id=unique_local_group_id,
            name="Unit with a pretty cool name",
        ),
        SaveIngredientUnit(
            group_id=unique_local_group_id,
            name="Unit with a correct horse battery staple",
        ),
    ]

    # Add a bunch of units for stable randomization
    units.extend(
        [
            SaveIngredientUnit(group_id=unique_local_group_id, name=f"{random_string()} unit")
            for _ in range(random_int(12, 20))
        ]
    )

    return database.ingredient_units.create_many(units)


@pytest.mark.parametrize(
    "search, expected_names",
    [
        (random_string(), []),
        ("Cup", ["Cup"]),
        ("tbsp", ["Table Spoon"]),
        ("very cool name", ["Unit with a very cool name", "Unit with a pretty cool name"]),
        ('"Tea Spoon"', ["Tea Spoon"]),
        ("correct staple", ["Unit with a correct horse battery staple"]),
    ],
    ids=[
        "no_match",
        "search_by_name",
        "search_by_unit",
        "match_order",
        "literal_search",
        "token_separation",
    ],
)
def test_basic_search(
    search: str,
    expected_names: list[str],
    database: AllRepositories,
    search_units: list[IngredientUnit],  # required so database is populated
    unique_local_group_id: str,
):
    repo = database.ingredient_units.by_group(unique_local_group_id)
    pagination = PaginationQuery(page=1, per_page=-1, order_by="created_at", order_direction=OrderDirection.asc)
    results = repo.page_all(pagination, search=search).items

    if len(expected_names) == 0:
        assert len(results) == 0
    else:
        # if more results are returned, that's acceptable, as long as they are ranked correctly
        assert len(results) >= len(expected_names)
        for unit, name in zip(results, expected_names, strict=False):
            assert unit.name == name


def test_fuzzy_search(
    database: AllRepositories,
    search_units: list[IngredientUnit],  # required so database is populated
    unique_local_group_id: str,
):
    # this only works on postgres
    if database.session.get_bind().name != "postgresql":
        return

    repo = database.ingredient_units.by_group(unique_local_group_id)
    pagination = PaginationQuery(page=1, per_page=-1, order_by="created_at", order_direction=OrderDirection.asc)
    results = repo.page_all(pagination, search="tabel spoone").items

    assert results and results[0].name == "Table Spoon"


def test_random_order_search(
    database: AllRepositories,
    search_units: list[IngredientUnit],  # required so database is populated
    unique_local_group_id: str,
):
    repo = database.ingredient_units.by_group(unique_local_group_id)
    pagination = PaginationQuery(
        page=1,
        per_page=-1,
        order_by="random",
        pagination_seed=str(datetime.now(timezone.utc)),
        order_direction=OrderDirection.asc,
    )
    random_ordered = []
    for _ in range(5):
        pagination.pagination_seed = str(datetime.now(timezone.utc))
        random_ordered.append(repo.page_all(pagination, search="unit").items)
    assert not all(i == random_ordered[0] for i in random_ordered)
