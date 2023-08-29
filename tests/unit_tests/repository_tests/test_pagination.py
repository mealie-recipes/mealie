import random
import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from random import randint
from urllib.parse import parse_qsl, urlsplit

import pytest
from fastapi.testclient import TestClient
from humps import camelize

from mealie.repos.repository_factory import AllRepositories
from mealie.repos.repository_units import RepositoryUnit
from mealie.schema.labels.multi_purpose_label import MultiPurposeLabelSave
from mealie.schema.meal_plan.new_meal import CreatePlanEntry
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe_category import CategorySave, TagSave
from mealie.schema.recipe.recipe_ingredient import IngredientUnit, SaveIngredientFood, SaveIngredientUnit
from mealie.schema.recipe.recipe_tool import RecipeToolSave
from mealie.schema.response.pagination import OrderDirection, PaginationQuery
from mealie.services.seeder.seeder_service import SeederService
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


class Reversor:
    """
    Enables reversed sorting

    https://stackoverflow.com/a/56842689
    """

    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return other.obj == self.obj

    def __lt__(self, other):
        return other.obj < self.obj


def test_repository_pagination(database: AllRepositories, unique_user: TestUser):
    group = database.groups.get_one(unique_user.group_id)
    assert group

    seeder = SeederService(database, None, group)  # type: ignore
    seeder.seed_foods("en-US")

    foods_repo = database.ingredient_foods.by_group(unique_user.group_id)  # type: ignore

    query = PaginationQuery(
        page=1,
        order_by="id",
        per_page=10,
    )

    seen = []

    for _ in range(10):
        results = foods_repo.page_all(query)

        assert len(results.items) == 10

        for result in results.items:
            assert result.id not in seen

        seen += [result.id for result in results.items]

        query.page += 1

    results = foods_repo.page_all(query)

    for result in results.items:
        assert result.id not in seen


def test_pagination_response_and_metadata(database: AllRepositories, unique_user: TestUser):
    group = database.groups.get_one(unique_user.group_id)
    assert group

    seeder = SeederService(database, None, group)  # type: ignore
    seeder.seed_foods("en-US")

    foods_repo = database.ingredient_foods.by_group(unique_user.group_id)  # type: ignore

    # this should get all results
    query = PaginationQuery(
        page=1,
        per_page=-1,
    )

    all_results = foods_repo.page_all(query)
    assert all_results.total == len(all_results.items)

    # this should get the last page of results
    query = PaginationQuery(
        page=-1,
        per_page=1,
    )

    last_page_of_results = foods_repo.page_all(query)
    assert last_page_of_results.page == last_page_of_results.total_pages
    assert last_page_of_results.items[-1] == all_results.items[-1]


def test_pagination_guides(database: AllRepositories, unique_user: TestUser):
    group = database.groups.get_one(unique_user.group_id)
    assert group

    seeder = SeederService(database, None, group)  # type: ignore
    seeder.seed_foods("en-US")

    foods_repo = database.ingredient_foods.by_group(unique_user.group_id)  # type: ignore
    foods_route = (
        "/foods"  # this doesn't actually have to be accurate, it's just a placeholder to test for query params
    )

    query = PaginationQuery(page=1, per_page=1)

    first_page_of_results = foods_repo.page_all(query)
    first_page_of_results.set_pagination_guides(foods_route, query.dict())
    assert first_page_of_results.next is not None
    assert first_page_of_results.previous is None

    query = PaginationQuery(page=-1, per_page=1)

    last_page_of_results = foods_repo.page_all(query)
    last_page_of_results.set_pagination_guides(foods_route, query.dict())
    assert last_page_of_results.next is None
    assert last_page_of_results.previous is not None

    random_page = randint(2, first_page_of_results.total_pages - 1)
    query = PaginationQuery(page=random_page, per_page=1, filter_string="createdAt>2021-02-22")

    random_page_of_results = foods_repo.page_all(query)
    random_page_of_results.set_pagination_guides(foods_route, query.dict())

    next_params: dict = dict(parse_qsl(urlsplit(random_page_of_results.next).query))  # type: ignore
    assert int(next_params["page"]) == random_page + 1

    prev_params: dict = dict(parse_qsl(urlsplit(random_page_of_results.previous).query))  # type: ignore
    assert int(prev_params["page"]) == random_page - 1

    source_params = camelize(query.dict())
    for source_param in source_params:
        assert source_param in next_params
        assert source_param in prev_params


@pytest.fixture(scope="function")
def query_units(database: AllRepositories, unique_user: TestUser):
    unit_1 = database.ingredient_units.create(
        SaveIngredientUnit(name="test unit 1", group_id=unique_user.group_id, use_abbreviation=True)
    )

    # wait a moment so we can test datetime filters
    time.sleep(0.25)

    unit_2 = database.ingredient_units.create(
        SaveIngredientUnit(name="test unit 2", group_id=unique_user.group_id, use_abbreviation=False)
    )

    # wait a moment so we can test datetime filters
    time.sleep(0.25)

    unit_3 = database.ingredient_units.create(
        SaveIngredientUnit(name="test unit 3", group_id=unique_user.group_id, use_abbreviation=False)
    )

    unit_ids = [unit.id for unit in [unit_1, unit_2, unit_3]]
    units_repo = database.ingredient_units.by_group(unique_user.group_id)  # type: ignore

    # make sure we can get all of our test units
    query = PaginationQuery(page=1, per_page=-1)
    all_units = units_repo.page_all(query).items
    assert len(all_units) == 3

    for unit in all_units:
        assert unit.id in unit_ids

    yield units_repo, unit_1, unit_2, unit_3

    for unit_id in unit_ids:
        units_repo.delete(unit_id)


def test_pagination_filter_basic(query_units: tuple[RepositoryUnit, IngredientUnit, IngredientUnit, IngredientUnit]):
    units_repo = query_units[0]
    unit_2 = query_units[2]

    query = PaginationQuery(page=1, per_page=-1, query_filter='name="test unit 2"')
    unit_results = units_repo.page_all(query).items
    assert len(unit_results) == 1
    assert unit_results[0].id == unit_2.id


def test_pagination_filter_null(database: AllRepositories, unique_user: TestUser):
    recipe_not_made_1 = database.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=random_string())
    )
    recipe_not_made_2 = database.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=random_string())
    )

    # give one recipe a last made date
    recipe_made = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id, group_id=unique_user.group_id, name=random_string(), last_made=datetime.now()
        )
    )

    recipe_repo = database.recipes.by_group(unique_user.group_id)  # type: ignore

    query = PaginationQuery(page=1, per_page=-1, query_filter="lastMade IS NONE")
    recipe_results = recipe_repo.page_all(query).items
    assert len(recipe_results) == 2
    result_ids = {result.id for result in recipe_results}
    assert recipe_not_made_1.id in result_ids
    assert recipe_not_made_2.id in result_ids
    assert recipe_made.id not in result_ids

    query = PaginationQuery(page=1, per_page=-1, query_filter="lastMade IS NULL")
    recipe_results = recipe_repo.page_all(query).items
    assert len(recipe_results) == 2
    result_ids = {result.id for result in recipe_results}
    assert recipe_not_made_1.id in result_ids
    assert recipe_not_made_2.id in result_ids
    assert recipe_made.id not in result_ids

    query = PaginationQuery(page=1, per_page=-1, query_filter="lastMade IS NOT NONE")
    recipe_results = recipe_repo.page_all(query).items
    assert len(recipe_results) == 1
    result_ids = {result.id for result in recipe_results}
    assert recipe_not_made_1.id not in result_ids
    assert recipe_not_made_2.id not in result_ids
    assert recipe_made.id in result_ids

    query = PaginationQuery(page=1, per_page=-1, query_filter="lastMade IS NOT NULL")
    recipe_results = recipe_repo.page_all(query).items
    assert len(recipe_results) == 1
    result_ids = {result.id for result in recipe_results}
    assert recipe_not_made_1.id not in result_ids
    assert recipe_not_made_2.id not in result_ids
    assert recipe_made.id in result_ids


def test_pagination_filter_in(query_units: tuple[RepositoryUnit, IngredientUnit, IngredientUnit, IngredientUnit]):
    units_repo, unit_1, unit_2, unit_3 = query_units

    query = PaginationQuery(page=1, per_page=-1, query_filter=f"name IN [{unit_1.name}, {unit_2.name}]")
    unit_results = units_repo.page_all(query).items

    assert len(unit_results) == 2
    result_ids = {unit.id for unit in unit_results}
    assert unit_1.id in result_ids
    assert unit_2.id in result_ids
    assert unit_3.id not in result_ids

    query = PaginationQuery(page=1, per_page=-1, query_filter=f"name NOT IN [{unit_1.name}, {unit_2.name}]")
    unit_results = units_repo.page_all(query).items

    assert len(unit_results) == 1
    result_ids = {unit.id for unit in unit_results}
    assert unit_1.id not in result_ids
    assert unit_2.id not in result_ids
    assert unit_3.id in result_ids

    query = PaginationQuery(page=1, per_page=-1, query_filter=f'name IN ["{unit_3.name}"]')
    unit_results = units_repo.page_all(query).items

    assert len(unit_results) == 1
    result_ids = {unit.id for unit in unit_results}
    assert unit_1.id not in result_ids
    assert unit_2.id not in result_ids
    assert unit_3.id in result_ids


def test_pagination_filter_in_advanced(database: AllRepositories, unique_user: TestUser):
    slug1, slug2 = (random_string(10) for _ in range(2))

    tags = [
        TagSave(group_id=unique_user.group_id, name=slug1, slug=slug1),
        TagSave(group_id=unique_user.group_id, name=slug2, slug=slug2),
    ]

    tag_1, tag_2 = [database.tags.create(tag) for tag in tags]

    # Bootstrap the database with recipes
    slug = random_string()
    recipe_0 = database.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=slug, slug=slug, tags=[])
    )

    slug = random_string()
    recipe_1 = database.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=slug, slug=slug, tags=[tag_1])
    )

    slug = random_string()
    recipe_2 = database.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=slug, slug=slug, tags=[tag_2])
    )

    slug = random_string()
    recipe_1_2 = database.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=slug, slug=slug, tags=[tag_1, tag_2])
    )

    query = PaginationQuery(page=1, per_page=-1, query_filter=f"tags.name IN [{tag_1.name}]")
    recipe_results = database.recipes.page_all(query).items
    assert len(recipe_results) == 2
    recipe_ids = {recipe.id for recipe in recipe_results}
    assert recipe_0.id not in recipe_ids
    assert recipe_1.id in recipe_ids
    assert recipe_2.id not in recipe_ids
    assert recipe_1_2.id in recipe_ids

    query = PaginationQuery(page=1, per_page=-1, query_filter=f"tags.name IN [{tag_1.name}, {tag_2.name}]")
    recipe_results = database.recipes.page_all(query).items
    assert len(recipe_results) == 3
    recipe_ids = {recipe.id for recipe in recipe_results}
    assert recipe_0.id not in recipe_ids
    assert recipe_1.id in recipe_ids
    assert recipe_2.id in recipe_ids
    assert recipe_1_2.id in recipe_ids

    query = PaginationQuery(page=1, per_page=-1, query_filter=f"tags.name CONTAINS ALL [{tag_1.name}, {tag_2.name}]")
    recipe_results = database.recipes.page_all(query).items
    assert len(recipe_results) == 1
    recipe_ids = {recipe.id for recipe in recipe_results}
    assert recipe_0.id not in recipe_ids
    assert recipe_1.id not in recipe_ids
    assert recipe_2.id not in recipe_ids
    assert recipe_1_2.id in recipe_ids


def test_pagination_filter_like(query_units: tuple[RepositoryUnit, IngredientUnit, IngredientUnit, IngredientUnit]):
    units_repo, unit_1, unit_2, unit_3 = query_units

    query = PaginationQuery(page=1, per_page=-1, query_filter=r'name LIKE "test u_it%"')
    unit_results = units_repo.page_all(query).items

    assert len(unit_results) == 3
    result_ids = {unit.id for unit in unit_results}
    assert unit_1.id in result_ids
    assert unit_2.id in result_ids
    assert unit_3.id in result_ids

    query = PaginationQuery(page=1, per_page=-1, query_filter=r'name LIKE "%unit 1"')
    unit_results = units_repo.page_all(query).items

    assert len(unit_results) == 1
    result_ids = {unit.id for unit in unit_results}
    assert unit_1.id in result_ids
    assert unit_2.id not in result_ids
    assert unit_3.id not in result_ids

    query = PaginationQuery(page=1, per_page=-1, query_filter=r'name NOT LIKE %t_1"')
    unit_results = units_repo.page_all(query).items

    assert len(unit_results) == 2
    result_ids = {unit.id for unit in unit_results}
    assert unit_1.id not in result_ids
    assert unit_2.id in result_ids
    assert unit_3.id in result_ids


def test_pagination_filter_keyword_namespace_conflict(database: AllRepositories, unique_user: TestUser):
    recipe_rating_1 = database.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=random_string(), rating=1)
    )
    recipe_rating_2 = database.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=random_string(), rating=2)
    )

    recipe_rating_3 = database.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=random_string(), rating=3)
    )

    recipe_repo = database.recipes.by_group(unique_user.group_id)  # type: ignore

    # "rating" contains the word "in", but we should not parse this as the keyword "IN"
    query = PaginationQuery(page=1, per_page=-1, query_filter="rating > 2")
    recipe_results = recipe_repo.page_all(query).items

    assert len(recipe_results) == 1
    result_ids = {recipe.id for recipe in recipe_results}
    assert recipe_rating_1.id not in result_ids
    assert recipe_rating_2.id not in result_ids
    assert recipe_rating_3.id in result_ids

    query = PaginationQuery(page=1, per_page=-1, query_filter="rating in [1, 3]")
    recipe_results = recipe_repo.page_all(query).items

    assert len(recipe_results) == 2
    result_ids = {recipe.id for recipe in recipe_results}
    assert recipe_rating_1.id in result_ids
    assert recipe_rating_2.id not in result_ids
    assert recipe_rating_3.id in result_ids


def test_pagination_filter_logical_namespace_conflict(database: AllRepositories, unique_user: TestUser):
    categories = [
        CategorySave(group_id=unique_user.group_id, name=random_string(10)),
        CategorySave(group_id=unique_user.group_id, name=random_string(10)),
    ]
    category_1, category_2 = [database.categories.create(category) for category in categories]

    # Bootstrap the database with recipes
    slug = random_string()
    recipe_category_0 = database.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=slug, slug=slug)
    )

    slug = random_string()
    recipe_category_1 = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug,
            slug=slug,
            recipe_category=[category_1],
        )
    )

    slug = random_string()
    recipe_category_2 = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug,
            slug=slug,
            recipe_category=[category_2],
        )
    )

    # "recipeCategory" has the substring "or" in it, which shouldn't break queries
    query = PaginationQuery(page=1, per_page=-1, query_filter=f'recipeCategory.id = "{category_1.id}"')
    recipe_results = database.recipes.by_group(unique_user.group_id).page_all(query).items  # type: ignore
    assert len(recipe_results) == 1
    recipe_ids = {recipe.id for recipe in recipe_results}
    assert recipe_category_0.id not in recipe_ids
    assert recipe_category_1.id in recipe_ids
    assert recipe_category_2.id not in recipe_ids


def test_pagination_filter_datetimes(
    query_units: tuple[RepositoryUnit, IngredientUnit, IngredientUnit, IngredientUnit]
):
    # units are created in order with increasing createdAt values
    units_repo, unit_1, unit_2, unit_3 = query_units

    ## GT
    past_dt: datetime = unit_1.created_at - timedelta(seconds=1)  # type: ignore
    dt = past_dt.isoformat()
    query = PaginationQuery(page=1, per_page=-1, query_filter=f'createdAt>"{dt}"')
    unit_results = units_repo.page_all(query).items
    unit_ids = set(unit.id for unit in unit_results)
    assert len(unit_ids) == 3
    assert unit_1.id in unit_ids
    assert unit_2.id in unit_ids
    assert unit_3.id in unit_ids

    dt = unit_1.created_at.isoformat()  # type: ignore
    query = PaginationQuery(page=1, per_page=-1, query_filter=f'createdAt>"{dt}"')
    unit_results = units_repo.page_all(query).items
    unit_ids = set(unit.id for unit in unit_results)
    assert len(unit_ids) == 2
    assert unit_1.id not in unit_ids
    assert unit_2.id in unit_ids
    assert unit_3.id in unit_ids

    dt = unit_2.created_at.isoformat()  # type: ignore
    query = PaginationQuery(page=1, per_page=-1, query_filter=f'createdAt>"{dt}"')
    unit_results = units_repo.page_all(query).items
    unit_ids = set(unit.id for unit in unit_results)
    assert len(unit_ids) == 1
    assert unit_1.id not in unit_ids
    assert unit_2.id not in unit_ids
    assert unit_3.id in unit_ids

    dt = unit_3.created_at.isoformat()  # type: ignore
    query = PaginationQuery(page=1, per_page=-1, query_filter=f'createdAt>"{dt}"')
    unit_results = units_repo.page_all(query).items
    unit_ids = set(unit.id for unit in unit_results)
    assert len(unit_ids) == 0

    future_dt: datetime = unit_3.created_at + timedelta(seconds=1)  # type: ignore
    dt = future_dt.isoformat()
    query = PaginationQuery(page=1, per_page=-1, query_filter=f'createdAt>"{dt}"')
    unit_results = units_repo.page_all(query).items
    unit_ids = set(unit.id for unit in unit_results)
    assert len(unit_ids) == 0

    ## GTE
    past_dt = unit_1.created_at - timedelta(seconds=1)  # type: ignore
    dt = past_dt.isoformat()
    query = PaginationQuery(page=1, per_page=-1, query_filter=f'createdAt>="{dt}"')
    unit_results = units_repo.page_all(query).items
    unit_ids = set(unit.id for unit in unit_results)
    assert len(unit_ids) == 3
    assert unit_1.id in unit_ids
    assert unit_2.id in unit_ids
    assert unit_3.id in unit_ids

    dt = unit_1.created_at.isoformat()  # type: ignore
    query = PaginationQuery(page=1, per_page=-1, query_filter=f'createdAt>="{dt}"')
    unit_results = units_repo.page_all(query).items
    unit_ids = set(unit.id for unit in unit_results)
    assert len(unit_ids) == 3
    assert unit_1.id in unit_ids
    assert unit_2.id in unit_ids
    assert unit_3.id in unit_ids

    dt = unit_2.created_at.isoformat()  # type: ignore
    query = PaginationQuery(page=1, per_page=-1, query_filter=f'createdAt>="{dt}"')
    unit_results = units_repo.page_all(query).items
    unit_ids = set(unit.id for unit in unit_results)
    assert len(unit_ids) == 2
    assert unit_1.id not in unit_ids
    assert unit_2.id in unit_ids
    assert unit_3.id in unit_ids

    dt = unit_3.created_at.isoformat()  # type: ignore
    query = PaginationQuery(page=1, per_page=-1, query_filter=f'createdAt>="{dt}"')
    unit_results = units_repo.page_all(query).items
    unit_ids = set(unit.id for unit in unit_results)
    assert len(unit_ids) == 1
    assert unit_1.id not in unit_ids
    assert unit_2.id not in unit_ids
    assert unit_3.id in unit_ids

    future_dt = unit_3.created_at + timedelta(seconds=1)  # type: ignore
    dt = future_dt.isoformat()
    query = PaginationQuery(page=1, per_page=-1, query_filter=f'createdAt>="{dt}"')
    unit_results = units_repo.page_all(query).items
    unit_ids = set(unit.id for unit in unit_results)
    assert len(unit_ids) == 0


@pytest.mark.parametrize("order_direction", [OrderDirection.asc, OrderDirection.desc], ids=["ascending", "descending"])
def test_pagination_order_by_multiple(
    database: AllRepositories, unique_user: TestUser, order_direction: OrderDirection
):
    current_time = datetime.now()

    alphabet = ["a", "b", "c", "d", "e"]
    abbreviations = alphabet.copy()
    descriptions = alphabet.copy()

    random.shuffle(abbreviations)
    random.shuffle(descriptions)
    assert abbreviations != descriptions

    units_to_create: list[SaveIngredientUnit] = []
    for abbreviation in abbreviations:
        for description in descriptions:
            units_to_create.append(
                SaveIngredientUnit(
                    group_id=unique_user.group_id,
                    name=random_string(),
                    abbreviation=abbreviation,
                    description=description,
                )
            )

    sorted_units = database.ingredient_units.create_many(units_to_create)
    sorted_units.sort(key=lambda x: (x.abbreviation, x.description), reverse=order_direction is OrderDirection.desc)

    query = database.ingredient_units.page_all(
        PaginationQuery(
            page=1,
            per_page=-1,
            order_by="abbreviation, description",
            order_direction=order_direction,
            query_filter=f'created_at >= "{current_time.isoformat()}"',
        )
    )

    assert query.items == sorted_units


@pytest.mark.parametrize(
    "order_by_str, order_direction",
    [
        ("abbreviation:asc, description:desc", OrderDirection.asc),
        ("abbreviation:asc, description:desc", OrderDirection.desc),
        ("abbreviation, description:desc", OrderDirection.asc),
        ("abbreviation:asc, description", OrderDirection.desc),
    ],
    ids=[
        "order_by_asc_explicit_order_bys",
        "order_by_desc_explicit_order_bys",
        "order_by_asc_inferred_order_by",
        "order_by_desc_inferred_order_by",
    ],
)
def test_pagination_order_by_multiple_directions(
    database: AllRepositories, unique_user: TestUser, order_by_str: str, order_direction: OrderDirection
):
    current_time = datetime.now()

    alphabet = ["a", "b", "c", "d", "e"]
    abbreviations = alphabet.copy()
    descriptions = alphabet.copy()

    random.shuffle(abbreviations)
    random.shuffle(descriptions)
    assert abbreviations != descriptions

    units_to_create: list[SaveIngredientUnit] = []
    for abbreviation in abbreviations:
        for description in descriptions:
            units_to_create.append(
                SaveIngredientUnit(
                    group_id=unique_user.group_id,
                    name=random_string(),
                    abbreviation=abbreviation,
                    description=description,
                )
            )

    sorted_units = database.ingredient_units.create_many(units_to_create)

    # sort by abbreviation ascending, description descending
    sorted_units.sort(key=lambda x: (x.abbreviation, Reversor(x.description)))

    query = database.ingredient_units.page_all(
        PaginationQuery(
            page=1,
            per_page=-1,
            order_by=order_by_str,
            order_direction=order_direction,
            query_filter=f'created_at >= "{current_time.isoformat()}"',
        )
    )

    assert query.items == sorted_units


@pytest.mark.parametrize(
    "order_direction",
    [OrderDirection.asc, OrderDirection.desc],
    ids=["order_ascending", "order_descending"],
)
def test_pagination_order_by_nested_model(
    database: AllRepositories, unique_user: TestUser, order_direction: OrderDirection
):
    current_time = datetime.now()

    alphabet = ["a", "b", "c", "d", "e"]
    labels = database.group_multi_purpose_labels.create_many(
        [MultiPurposeLabelSave(group_id=unique_user.group_id, name=letter) for letter in alphabet]
    )
    random.shuffle(labels)

    sorted_foods = database.ingredient_foods.create_many(
        [SaveIngredientFood(group_id=unique_user.group_id, name=random_string(), label_id=label.id) for label in labels]
    )

    sorted_foods.sort(key=lambda x: x.label.name, reverse=order_direction is OrderDirection.desc)  # type: ignore
    query = database.ingredient_foods.page_all(
        PaginationQuery(
            page=1,
            per_page=-1,
            order_by="label.name",
            order_direction=order_direction,
            query_filter=f'created_at >= "{current_time.isoformat()}"',
        )
    )

    assert query.items == sorted_foods


def test_pagination_filter_dates(api_client: TestClient, unique_user: TestUser):
    yesterday = date.today() - timedelta(days=1)
    today = date.today()
    tomorrow = date.today() + timedelta(days=1)
    day_after_tomorrow = date.today() + timedelta(days=2)

    mealplan_today = CreatePlanEntry(date=today, entry_type="breakfast", title=random_string(), text=random_string())
    mealplan_tomorrow = CreatePlanEntry(
        date=tomorrow, entry_type="breakfast", title=random_string(), text=random_string()
    )

    for mealplan_to_create in [mealplan_today, mealplan_tomorrow]:
        data = mealplan_to_create.dict()
        data["date"] = data["date"].strftime("%Y-%m-%d")
        response = api_client.post(api_routes.groups_mealplans, json=data, headers=unique_user.token)
        assert response.status_code == 201

    ## Yesterday
    params = {f"page": 1, "perPage": -1, "queryFilter": f"date >= {yesterday.strftime('%Y-%m-%d')}"}
    response = api_client.get(api_routes.groups_mealplans, params=params, headers=unique_user.token)
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json["items"]) == 2
    fetched_mealplan_titles = set(mp["title"] for mp in response_json["items"])
    assert mealplan_today.title in fetched_mealplan_titles
    assert mealplan_tomorrow.title in fetched_mealplan_titles

    params = {f"page": 1, "perPage": -1, "queryFilter": f"date > {yesterday.strftime('%Y-%m-%d')}"}
    response = api_client.get(api_routes.groups_mealplans, params=params, headers=unique_user.token)
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json["items"]) == 2
    fetched_mealplan_titles = set(mp["title"] for mp in response_json["items"])
    assert mealplan_today.title in fetched_mealplan_titles
    assert mealplan_tomorrow.title in fetched_mealplan_titles

    ## Today
    params = {f"page": 1, "perPage": -1, "queryFilter": f"date >= {today.strftime('%Y-%m-%d')}"}
    response = api_client.get(api_routes.groups_mealplans, params=params, headers=unique_user.token)
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json["items"]) == 2
    fetched_mealplan_titles = set(mp["title"] for mp in response_json["items"])
    assert mealplan_today.title in fetched_mealplan_titles
    assert mealplan_tomorrow.title in fetched_mealplan_titles

    params = {f"page": 1, "perPage": -1, "queryFilter": f"date > {today.strftime('%Y-%m-%d')}"}
    response = api_client.get(api_routes.groups_mealplans, params=params, headers=unique_user.token)
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json["items"]) == 1
    fetched_mealplan_titles = set(mp["title"] for mp in response_json["items"])
    assert mealplan_today.title not in fetched_mealplan_titles
    assert mealplan_tomorrow.title in fetched_mealplan_titles

    ## Tomorrow
    params = {f"page": 1, "perPage": -1, "queryFilter": f"date >= {tomorrow.strftime('%Y-%m-%d')}"}
    response = api_client.get(api_routes.groups_mealplans, params=params, headers=unique_user.token)
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json["items"]) == 1
    fetched_mealplan_titles = set(mp["title"] for mp in response_json["items"])
    assert mealplan_today.title not in fetched_mealplan_titles
    assert mealplan_tomorrow.title in fetched_mealplan_titles

    params = {f"page": 1, "perPage": -1, "queryFilter": f"date > {tomorrow.strftime('%Y-%m-%d')}"}
    response = api_client.get(api_routes.groups_mealplans, params=params, headers=unique_user.token)
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json["items"]) == 0

    ## Day After Tomorrow
    params = {f"page": 1, "perPage": -1, "queryFilter": f"date >= {day_after_tomorrow.strftime('%Y-%m-%d')}"}
    response = api_client.get(api_routes.groups_mealplans, params=params, headers=unique_user.token)
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json["items"]) == 0

    params = {f"page": 1, "perPage": -1, "queryFilter": f"date > {day_after_tomorrow.strftime('%Y-%m-%d')}"}
    response = api_client.get(api_routes.groups_mealplans, params=params, headers=unique_user.token)
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json["items"]) == 0


def test_pagination_filter_booleans(query_units: tuple[RepositoryUnit, IngredientUnit, IngredientUnit, IngredientUnit]):
    units_repo = query_units[0]
    unit_1 = query_units[1]

    query = PaginationQuery(page=1, per_page=-1, query_filter="useAbbreviation=true")
    unit_results = units_repo.page_all(query).items
    assert len(unit_results) == 1
    assert unit_results[0].id == unit_1.id


def test_pagination_filter_advanced(query_units: tuple[RepositoryUnit, IngredientUnit, IngredientUnit, IngredientUnit]):
    units_repo, unit_1, unit_2, unit_3 = query_units

    dt = str(unit_3.created_at.isoformat())  # type: ignore
    qf = f'name="test unit 1" OR (useAbbreviation=f AND (name="{unit_2.name}" OR createdAt > "{dt}"))'
    query = PaginationQuery(page=1, per_page=-1, query_filter=qf)
    unit_results = units_repo.page_all(query).items

    assert len(unit_results) == 2
    result_ids = {unit.id for unit in unit_results}
    assert unit_1.id in result_ids
    assert unit_2.id in result_ids
    assert unit_3.id not in result_ids

    qf = f'(name LIKE %_1 OR name IN ["{unit_2.name}"]) AND createdAt IS NOT NONE'
    query = PaginationQuery(page=1, per_page=-1, query_filter=qf)
    unit_results = units_repo.page_all(query).items

    assert len(unit_results) == 2
    result_ids = {unit.id for unit in unit_results}
    assert unit_1.id in result_ids
    assert unit_2.id in result_ids
    assert unit_3.id not in result_ids


def test_pagination_filter_advanced_frontend_sort(database: AllRepositories, unique_user: TestUser):
    categories = [
        CategorySave(group_id=unique_user.group_id, name=random_string(10)),
        CategorySave(group_id=unique_user.group_id, name=random_string(10)),
    ]
    category_1, category_2 = [database.categories.create(category) for category in categories]

    slug1, slug2 = (random_string(10) for _ in range(2))
    tags = [
        TagSave(group_id=unique_user.group_id, name=slug1, slug=slug1),
        TagSave(group_id=unique_user.group_id, name=slug2, slug=slug2),
    ]
    tag_1, tag_2 = [database.tags.create(tag) for tag in tags]

    tools = [
        RecipeToolSave(group_id=unique_user.group_id, name=random_string(10)),
        RecipeToolSave(group_id=unique_user.group_id, name=random_string(10)),
    ]
    tool_1, tool_2 = [database.tools.create(tool) for tool in tools]

    # Bootstrap the database with recipes
    slug = random_string()
    recipe_ct0_tg0_tl0 = database.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=slug, slug=slug)
    )

    slug = random_string()
    recipe_ct1_tg0_tl0 = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug,
            slug=slug,
            recipe_category=[category_1],
        )
    )

    slug = random_string()
    recipe_ct12_tg0_tl0 = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug,
            slug=slug,
            recipe_category=[category_1, category_2],
        )
    )

    slug = random_string()
    recipe_ct1_tg1_tl0 = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug,
            slug=slug,
            recipe_category=[category_1],
            tags=[tag_1],
        )
    )

    slug = random_string()
    recipe_ct1_tg0_tl1 = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug,
            slug=slug,
            recipe_category=[category_1],
            tools=[tool_1],
        )
    )

    slug = random_string()
    recipe_ct0_tg2_tl2 = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug,
            slug=slug,
            tags=[tag_2],
            tools=[tool_2],
        )
    )

    slug = random_string()
    recipe_ct12_tg12_tl2 = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug,
            slug=slug,
            recipe_category=[category_1, category_2],
            tags=[tag_1, tag_2],
            tools=[tool_2],
        )
    )

    repo = database.recipes.by_group(unique_user.group_id)  # type: ignore

    qf = f'recipeCategory.id IN ["{category_1.id}"] AND tools.id IN ["{tool_1.id}"]'
    query = PaginationQuery(page=1, per_page=-1, query_filter=qf)
    recipe_results = repo.page_all(query).items
    assert len(recipe_results) == 1
    recipe_ids = {recipe.id for recipe in recipe_results}
    assert recipe_ct0_tg0_tl0.id not in recipe_ids
    assert recipe_ct1_tg0_tl0.id not in recipe_ids
    assert recipe_ct12_tg0_tl0.id not in recipe_ids
    assert recipe_ct1_tg1_tl0.id not in recipe_ids
    assert recipe_ct1_tg0_tl1.id in recipe_ids
    assert recipe_ct0_tg2_tl2.id not in recipe_ids
    assert recipe_ct12_tg12_tl2.id not in recipe_ids

    qf = f'recipeCategory.id CONTAINS ALL ["{category_1.id}", "{category_2.id}"] AND tags.id IN ["{tag_1.id}"]'
    query = PaginationQuery(page=1, per_page=-1, query_filter=qf)
    recipe_results = repo.page_all(query).items
    assert len(recipe_results) == 1
    recipe_ids = {recipe.id for recipe in recipe_results}
    assert recipe_ct0_tg0_tl0.id not in recipe_ids
    assert recipe_ct1_tg0_tl0.id not in recipe_ids
    assert recipe_ct12_tg0_tl0.id not in recipe_ids
    assert recipe_ct1_tg1_tl0.id not in recipe_ids
    assert recipe_ct1_tg0_tl1.id not in recipe_ids
    assert recipe_ct0_tg2_tl2.id not in recipe_ids
    assert recipe_ct12_tg12_tl2.id in recipe_ids

    qf = f'tags.id IN ["{tag_1.id}", "{tag_2.id}"] AND tools.id IN ["{tool_2.id}"]'
    query = PaginationQuery(page=1, per_page=-1, query_filter=qf)
    recipe_results = repo.page_all(query).items
    assert len(recipe_results) == 2
    recipe_ids = {recipe.id for recipe in recipe_results}
    assert recipe_ct0_tg0_tl0.id not in recipe_ids
    assert recipe_ct1_tg0_tl0.id not in recipe_ids
    assert recipe_ct12_tg0_tl0.id not in recipe_ids
    assert recipe_ct1_tg1_tl0.id not in recipe_ids
    assert recipe_ct1_tg0_tl1.id not in recipe_ids
    assert recipe_ct0_tg2_tl2.id in recipe_ids
    assert recipe_ct12_tg12_tl2.id in recipe_ids

    qf = (
        f'recipeCategory.id CONTAINS ALL ["{category_1.id}", "{category_2.id}"]'
        f'AND tags.id IN ["{tag_1.id}", "{tag_2.id}"] AND tools.id IN ["{tool_1.id}", "{tool_2.id}"]'
    )
    query = PaginationQuery(page=1, per_page=-1, query_filter=qf)
    recipe_results = repo.page_all(query).items
    assert len(recipe_results) == 1
    recipe_ids = {recipe.id for recipe in recipe_results}
    assert recipe_ct0_tg0_tl0.id not in recipe_ids
    assert recipe_ct1_tg0_tl0.id not in recipe_ids
    assert recipe_ct12_tg0_tl0.id not in recipe_ids
    assert recipe_ct1_tg1_tl0.id not in recipe_ids
    assert recipe_ct1_tg0_tl1.id not in recipe_ids
    assert recipe_ct0_tg2_tl2.id not in recipe_ids
    assert recipe_ct12_tg12_tl2.id in recipe_ids


@pytest.mark.parametrize(
    "qf",
    [
        pytest.param('(name="test name" AND useAbbreviation=f))', id="unbalanced parenthesis"),
        pytest.param('id="this is not a valid UUID"', id="invalid UUID"),
        pytest.param('createdAt="this is not a valid datetime format"', id="invalid datetime format"),
        pytest.param('name IS "test name"', id="IS can only be used with NULL or NONE"),
        pytest.param('name IS NOT "test name"', id="IS NOT can only be used with NULL or NONE"),
        pytest.param('name IN "test name"', id="IN must use a list of values"),
        pytest.param('name NOT IN "test name"', id="NOT IN must use a list of values"),
        pytest.param('name CONTAINS ALL "test name"', id="CONTAINS ALL must use a list of values"),
        pytest.param('createdAt LIKE "2023-02-25"', id="LIKE is only valid for string columns"),
        pytest.param('createdAt NOT LIKE "2023-02-25"', id="NOT LIKE is only valid for string columns"),
        pytest.param('badAttribute="test value"', id="invalid attribute"),
        pytest.param('group.badAttribute="test value"', id="bad nested attribute"),
        pytest.param('group.preferences.badAttribute="test value"', id="bad double nested attribute"),
    ],
)
def test_malformed_query_filters(api_client: TestClient, unique_user: TestUser, qf: str):
    # verify that improper queries throw 400 errors
    route = "/api/units"

    response = api_client.get(route, params={"queryFilter": qf}, headers=unique_user.token)
    assert response.status_code == 400


def test_pagination_filter_nested(api_client: TestClient, user_tuple: list[TestUser]):
    # create a few recipes for each user
    slugs: defaultdict[int, list[str]] = defaultdict(list)
    for i, user in enumerate(user_tuple):
        for _ in range(random_int(3, 5)):
            slug: str = random_string()
            response = api_client.post(api_routes.recipes, json={"name": slug}, headers=user.token)

            assert response.status_code == 201
            slugs[i].append(slug)

    # query recipes with a nested user filter
    recipe_ids: defaultdict[int, list[str]] = defaultdict(list)
    for i, user in enumerate(user_tuple):
        params = {"page": 1, "perPage": -1, "queryFilter": f'user.id="{user.user_id}"'}
        response = api_client.get(api_routes.recipes, params=params, headers=user.token)

        assert response.status_code == 200
        recipes_data: list[dict] = response.json()["items"]
        assert recipes_data

        for recipe_data in recipes_data:
            slug = recipe_data["slug"]
            assert slug in slugs[i]
            assert slug not in slugs[(i + 1) % len(user_tuple)]

            recipe_ids[i].append(recipe_data["id"])

    # query timeline events with a double nested recipe.user filter
    for i, user in enumerate(user_tuple):
        params = {"page": 1, "perPage": -1, "queryFilter": f'recipe.user.id="{user.user_id}"'}
        response = api_client.get(api_routes.recipes_timeline_events, params=params, headers=user.token)

        assert response.status_code == 200
        events_data: list[dict] = response.json()["items"]
        assert events_data

        for event_data in events_data:
            recipe_id = event_data["recipeId"]
            assert recipe_id in recipe_ids[i]
            assert recipe_id not in recipe_ids[(i + 1) % len(user_tuple)]
