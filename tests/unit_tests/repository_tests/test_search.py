from datetime import datetime

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe_ingredient import SaveIngredientUnit
from mealie.schema.response.pagination import OrderDirection, PaginationQuery
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


def test_search_filter(database: AllRepositories, unique_user: TestUser):
    units = [
        SaveIngredientUnit(
            group_id=unique_user.group_id,
            name="Tea Spoon",
            abbreviation="tsp",
        ),
        SaveIngredientUnit(
            group_id=unique_user.group_id,
            name="Table Spoon",
            description="unique description",
            abbreviation="tbsp",
        ),
        SaveIngredientUnit(
            group_id=unique_user.group_id,
            name="Cup",
            description="A bucket that's full",
        ),
        SaveIngredientUnit(
            group_id=unique_user.group_id,
            name="Píñch",
        ),
        SaveIngredientUnit(
            group_id=unique_user.group_id,
            name="Unit with a very cool name",
        ),
        SaveIngredientUnit(
            group_id=unique_user.group_id,
            name="Unit with a pretty cool name",
        ),
    ]

    # Add a bunch of units for stable randomization
    units.extend(
        [
            SaveIngredientUnit(group_id=unique_user.group_id, name=f"{random_string()} unit")
            for _ in range(random_int(12, 20))
        ]
    )

    units = database.ingredient_units.create_many(units)
    pagination_query = PaginationQuery(page=1, per_page=-1, order_by="created_at", order_direction=OrderDirection.asc)

    # No hits
    empty_result = database.ingredient_units.page_all(pagination_query, search=random_string(10)).items
    assert len(empty_result) == 0

    # Search by name
    name_result = database.ingredient_units.page_all(pagination_query, search="Cup").items
    assert len(name_result) == 1
    assert name_result[0].name == "Cup"

    # Search by abbreviation
    abbreviation_result = database.ingredient_units.page_all(pagination_query, search="tbsp").items
    assert len(abbreviation_result) == 1
    assert abbreviation_result[0].name == "Table Spoon"

    # Search by description
    description_result = database.ingredient_units.page_all(pagination_query, search="unique description").items
    assert len(description_result) == 1
    assert description_result[0].name == "Table Spoon"

    # Make sure title matches are ordered in front
    ordered_result = database.ingredient_units.page_all(pagination_query, search="very cool name").items
    assert len(ordered_result) == 2
    assert ordered_result[0].name == "Unit with a very cool name"
    assert ordered_result[1].name == "Unit with a pretty cool name"

    # Test literal search
    literal_result = database.ingredient_units.page_all(pagination_query, search='"Tea Spoon"').items
    assert len(literal_result) == 1
    assert literal_result[0].name == "Tea Spoon"

    # Test special character removal from non-literal searches
    character_result = database.ingredient_units.page_all(pagination_query, search="tea-spoon").items
    assert len(character_result) == 2
    assert character_result[0].name == "Tea Spoon"
    assert character_result[1].name == "Table Spoon"

    # Test token separation
    token_result = database.ingredient_units.page_all(pagination_query, search="full bucket").items
    assert len(token_result) == 1
    assert token_result[0].name == "Cup"

    # Test fuzzy search
    if database.session.get_bind().name == "postgresql":
        fuzzy_result = database.ingredient_units.page_all(pagination_query, search="taespoon").items
        assert len(fuzzy_result) == 1
        assert fuzzy_result[0].name == "Tea Spoon"

    # Test random ordering with search
    pagination_query = PaginationQuery(
        page=1,
        per_page=-1,
        order_by="random",
        pagination_seed=str(datetime.now()),
        order_direction=OrderDirection.asc,
    )
    random_ordered = []
    for _ in range(5):
        pagination_query.pagination_seed = str(datetime.now())
        random_ordered.append(database.ingredient_units.page_all(pagination_query, search="unit").items)
    assert not all(i == random_ordered[0] for i in random_ordered)
