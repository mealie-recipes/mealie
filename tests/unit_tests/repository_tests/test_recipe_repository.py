from datetime import datetime, timezone
from typing import cast
from uuid import UUID

import pytest

from mealie.repos.repository_factory import AllRepositories
from mealie.repos.repository_recipes import RepositoryRecipes
from mealie.schema.recipe import RecipeIngredient, SaveIngredientFood
from mealie.schema.recipe.recipe import Recipe, RecipeCategory, RecipeSummary
from mealie.schema.recipe.recipe_category import CategoryOut, CategorySave, TagSave
from mealie.schema.recipe.recipe_tool import RecipeToolSave
from mealie.schema.response import OrderDirection, PaginationQuery
from mealie.schema.user.user import GroupBase, UserRatingCreate
from tests.utils.factories import random_email, random_string
from tests.utils.fixture_schemas import TestUser


@pytest.fixture()
def unique_local_group_id(database: AllRepositories) -> str:
    return str(database.groups.create(GroupBase(name=random_string())).id)


@pytest.fixture()
def unique_local_user_id(database: AllRepositories, unique_local_group_id: str) -> str:
    return str(
        database.users.create(
            {
                "username": random_string(),
                "email": random_email(),
                "group_id": unique_local_group_id,
                "full_name": random_string(),
                "password": random_string(),
                "admin": False,
            }
        ).id
    )


@pytest.fixture()
def search_recipes(database: AllRepositories, unique_local_group_id: str, unique_local_user_id: str) -> list[Recipe]:
    recipes = [
        Recipe(
            user_id=unique_local_user_id,
            group_id=unique_local_group_id,
            name="Steinbock Sloop",
            description=f"My favorite horns are delicious",
            recipe_ingredient=[
                RecipeIngredient(note="alpine animal"),
            ],
        ),
        Recipe(
            user_id=unique_local_user_id,
            group_id=unique_local_group_id,
            name="Fiddlehead Fern Stir Fry",
            recipe_ingredient=[
                RecipeIngredient(note="moss"),
            ],
        ),
        Recipe(
            user_id=unique_local_user_id,
            group_id=unique_local_group_id,
            name="Animal Sloop",
        ),
        # Test diacritics
        Recipe(
            user_id=unique_local_user_id,
            group_id=unique_local_group_id,
            name="Rátàtôuile",
        ),
        # Add a bunch of recipes for stable randomization
        Recipe(
            user_id=unique_local_user_id,
            group_id=unique_local_group_id,
            name=f"{random_string(10)} soup",
        ),
        Recipe(
            user_id=unique_local_user_id,
            group_id=unique_local_group_id,
            name=f"{random_string(10)} soup",
        ),
        Recipe(
            user_id=unique_local_user_id,
            group_id=unique_local_group_id,
            name=f"{random_string(10)} soup",
        ),
        Recipe(
            user_id=unique_local_user_id,
            group_id=unique_local_group_id,
            name=f"{random_string(10)} soup",
        ),
        Recipe(
            user_id=unique_local_user_id,
            group_id=unique_local_group_id,
            name=f"{random_string(10)} soup",
        ),
        Recipe(
            user_id=unique_local_user_id,
            group_id=unique_local_group_id,
            name=f"{random_string(10)} soup",
        ),
    ]

    return database.recipes.create_many(recipes)


def test_recipe_repo_get_by_categories_basic(database: AllRepositories, unique_user: TestUser):
    # Bootstrap the database with categories
    slug1, slug2, slug3 = (random_string(10) for _ in range(3))

    categories: list[CategoryOut | CategorySave] = [
        CategorySave(group_id=unique_user.group_id, name=slug1, slug=slug1),
        CategorySave(group_id=unique_user.group_id, name=slug2, slug=slug2),
        CategorySave(group_id=unique_user.group_id, name=slug3, slug=slug3),
    ]

    created_categories: list[CategoryOut] = []

    for category in categories:
        model = database.categories.create(category)
        created_categories.append(model)

    # Bootstrap the database with recipes
    recipes: list[Recipe | RecipeSummary] = []

    for idx in range(15):
        if idx % 3 == 0:
            category = created_categories[0]
        elif idx % 3 == 1:
            category = created_categories[1]
        else:
            category = created_categories[2]

        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                recipe_category=[category],
            ),
        )

    created_recipes = []

    for recipe in recipes:
        models = database.recipes.create(cast(Recipe, recipe))
        created_recipes.append(models)

    # Get all recipes by category

    for category in created_categories:
        repo: RepositoryRecipes = database.recipes.by_group(unique_user.group_id)  # type: ignore
        recipes = repo.get_by_categories([cast(RecipeCategory, category)])

        assert len(recipes) == 5

        for recipe in recipes:
            found_cat = recipe.recipe_category[0]

            assert found_cat.name == category.name
            assert found_cat.slug == category.slug
            assert found_cat.id == category.id


def test_recipe_repo_get_by_categories_multi(database: AllRepositories, unique_user: TestUser):
    slug1, slug2 = (random_string(10) for _ in range(2))

    categories = [
        CategorySave(group_id=unique_user.group_id, name=slug1, slug=slug1),
        CategorySave(group_id=unique_user.group_id, name=slug2, slug=slug2),
    ]

    created_categories = []
    known_category_ids = []

    for category in categories:
        model = database.categories.create(category)
        created_categories.append(model)
        known_category_ids.append(model.id)

    # Bootstrap the database with recipes
    recipes = []

    for _ in range(10):
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                recipe_category=created_categories,
            ),
        )

        # Insert Non-Category Recipes
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
            )
        )

    for recipe in recipes:
        database.recipes.create(recipe)

    # Get all recipes by both categories
    repo: RepositoryRecipes = database.recipes.by_group(unique_local_group_id)  # type: ignore
    by_category = repo.get_by_categories(cast(list[RecipeCategory], created_categories))

    assert len(by_category) == 10
    for recipe_summary in by_category:
        for recipe_category in recipe_summary.recipe_category:
            assert recipe_category.id in known_category_ids


def test_recipe_repo_pagination_by_categories(database: AllRepositories, unique_user: TestUser):
    slug1, slug2 = (random_string(10) for _ in range(2))

    categories = [
        CategorySave(group_id=unique_user.group_id, name=slug1, slug=slug1),
        CategorySave(group_id=unique_user.group_id, name=slug2, slug=slug2),
    ]

    created_categories = [database.categories.create(category) for category in categories]

    # Bootstrap the database with recipes
    recipes = []

    for i in range(10):
        # None of the categories
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
            )
        )

        # Only one of the categories
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                recipe_category=[created_categories[i % 2]],
            ),
        )

        # Both of the categories
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                recipe_category=created_categories,
            )
        )

    for recipe in recipes:
        database.recipes.create(recipe)

    pagination_query = PaginationQuery(
        page=1,
        per_page=-1,
    )

    # Get all recipes with only one category by UUID
    category_id = created_categories[0].id
    recipes_with_one_category = database.recipes.page_all(pagination_query, categories=[category_id]).items
    assert len(recipes_with_one_category) == 15

    for recipe_summary in recipes_with_one_category:
        category_ids = [category.id for category in recipe_summary.recipe_category]
        assert category_id in category_ids

    # Get all recipes with only one category by slug
    category_slug = created_categories[1].slug
    recipes_with_one_category = database.recipes.page_all(pagination_query, categories=[category_slug]).items
    assert len(recipes_with_one_category) == 15

    for recipe_summary in recipes_with_one_category:
        category_slugs = [category.slug for category in recipe_summary.recipe_category]
        assert category_slug in category_slugs

    # Get all recipes with both categories
    recipes_with_both_categories = database.recipes.page_all(
        pagination_query, categories=[category.id for category in created_categories]
    ).items
    assert len(recipes_with_both_categories) == 10

    for recipe_summary in recipes_with_both_categories:
        category_ids = [category.id for category in recipe_summary.recipe_category]
        for category in created_categories:
            assert category.id in category_ids

    # Test random ordering with category filter
    pagination_query = PaginationQuery(
        page=1,
        per_page=-1,
        order_by="random",
        pagination_seed=str(datetime.now(timezone.utc)),
        order_direction=OrderDirection.asc,
    )
    random_ordered = []
    for i in range(5):
        pagination_query.pagination_seed = str(datetime.now(timezone.utc))
        random_ordered.append(database.recipes.page_all(pagination_query, categories=[category_slug]).items)
    assert not all(i == random_ordered[0] for i in random_ordered)


def test_recipe_repo_pagination_by_tags(database: AllRepositories, unique_user: TestUser):
    slug1, slug2 = (random_string(10) for _ in range(2))

    tags = [
        TagSave(group_id=unique_user.group_id, name=slug1, slug=slug1),
        TagSave(group_id=unique_user.group_id, name=slug2, slug=slug2),
    ]

    created_tags = [database.tags.create(tag) for tag in tags]

    # Bootstrap the database with recipes
    recipes = []

    for i in range(10):
        # None of the tags
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
            )
        )

        # Only one of the tags
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                tags=[created_tags[i % 2]],
            ),
        )

        # Both of the tags
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                tags=created_tags,
            )
        )

    for recipe in recipes:
        database.recipes.create(recipe)

    pagination_query = PaginationQuery(
        page=1,
        per_page=-1,
    )

    # Get all recipes with only one tag by UUID
    tag_id = created_tags[0].id
    recipes_with_one_tag = database.recipes.page_all(pagination_query, tags=[tag_id]).items
    assert len(recipes_with_one_tag) == 15

    for recipe_summary in recipes_with_one_tag:
        tag_ids = [tag.id for tag in recipe_summary.tags]
        assert tag_id in tag_ids

    # Get all recipes with only one tag by slug
    tag_slug = created_tags[1].slug
    recipes_with_one_tag = database.recipes.page_all(pagination_query, tags=[tag_slug]).items
    assert len(recipes_with_one_tag) == 15

    for recipe_summary in recipes_with_one_tag:
        tag_slugs = [tag.slug for tag in recipe_summary.tags]
        assert tag_slug in tag_slugs

    # Get all recipes with both tags
    recipes_with_both_tags = database.recipes.page_all(pagination_query, tags=[tag.id for tag in created_tags]).items
    assert len(recipes_with_both_tags) == 10

    for recipe_summary in recipes_with_both_tags:
        tag_ids = [tag.id for tag in recipe_summary.tags]
        for tag in created_tags:
            assert tag.id in tag_ids

    # Test random ordering with tag filter
    pagination_query = PaginationQuery(
        page=1,
        per_page=-1,
        order_by="random",
        pagination_seed=str(datetime.now(timezone.utc)),
        order_direction=OrderDirection.asc,
    )
    random_ordered = []
    for i in range(5):
        pagination_query.pagination_seed = str(datetime.now(timezone.utc))
        random_ordered.append(database.recipes.page_all(pagination_query, tags=[tag_slug]).items)
    assert len(random_ordered[0]) == 15
    assert not all(i == random_ordered[0] for i in random_ordered)


def test_recipe_repo_pagination_by_tools(database: AllRepositories, unique_user: TestUser):
    slug1, slug2 = (random_string(10) for _ in range(2))

    tools = [
        RecipeToolSave(group_id=unique_user.group_id, name=slug1, slug=slug1),
        RecipeToolSave(group_id=unique_user.group_id, name=slug2, slug=slug2),
    ]

    created_tools = [database.tools.create(tool) for tool in tools]

    # Bootstrap the database with recipes
    recipes = []

    for i in range(10):
        # None of the tools
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
            )
        )

        # Only one of the tools
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                tools=[created_tools[i % 2]],
            ),
        )

        # Both of the tools
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                tools=created_tools,
            )
        )

    for recipe in recipes:
        database.recipes.create(recipe)

    pagination_query = PaginationQuery(
        page=1,
        per_page=-1,
    )

    # Get all recipes with only one tool by UUID
    tool_id = created_tools[0].id
    recipes_with_one_tool = database.recipes.page_all(pagination_query, tools=[tool_id]).items
    assert len(recipes_with_one_tool) == 15

    for recipe_summary in recipes_with_one_tool:
        tool_ids = [tool.id for tool in recipe_summary.tools]
        assert tool_id in tool_ids

    # Get all recipes with only one tool by slug
    tool_slug = created_tools[1].slug
    recipes_with_one_tool = database.recipes.page_all(pagination_query, tools=[tool_slug]).items
    assert len(recipes_with_one_tool) == 15

    for recipe_summary in recipes_with_one_tool:
        tool_slugs = [tool.slug for tool in recipe_summary.tools]
        assert tool_slug in tool_slugs

    # Get all recipes with both tools
    recipes_with_both_tools = database.recipes.page_all(
        pagination_query, tools=[tool.id for tool in created_tools]
    ).items
    assert len(recipes_with_both_tools) == 10

    for recipe_summary in recipes_with_both_tools:
        tool_ids = [tool.id for tool in recipe_summary.tools]
        for tool in created_tools:
            assert tool.id in tool_ids

    # Test random ordering with tools filter
    pagination_query = PaginationQuery(
        page=1,
        per_page=-1,
        order_by="random",
        pagination_seed=str(datetime.now(timezone.utc)),
        order_direction=OrderDirection.asc,
    )
    random_ordered = []
    for i in range(5):
        pagination_query.pagination_seed = str(datetime.now(timezone.utc))
        random_ordered.append(database.recipes.page_all(pagination_query, tools=[tool_id]).items)
    assert len(random_ordered[0]) == 15
    assert not all(i == random_ordered[0] for i in random_ordered)


def test_recipe_repo_pagination_by_foods(database: AllRepositories, unique_user: TestUser):
    slug1, slug2 = (random_string(10) for _ in range(2))

    foods = [
        SaveIngredientFood(group_id=unique_user.group_id, name=slug1),
        SaveIngredientFood(group_id=unique_user.group_id, name=slug2),
    ]

    created_foods = [database.ingredient_foods.create(food) for food in foods]

    # Bootstrap the database with recipes
    recipes = []

    for i in range(10):
        # None of the foods
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
            )
        )

        # Only one of the foods
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                recipe_ingredient=[RecipeIngredient(food=created_foods[i % 2])],
            ),
        )

        # Both of the foods
        recipes.append(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                recipe_ingredient=[RecipeIngredient(food=created_foods[0]), RecipeIngredient(food=created_foods[1])],
            )
        )

    for recipe in recipes:
        database.recipes.create(recipe)

    pagination_query = PaginationQuery(
        page=1,
        per_page=-1,
    )

    # Get all recipes with only one food by UUID
    food_id = created_foods[0].id
    recipes_with_one_food = database.recipes.page_all(pagination_query, foods=[food_id]).items
    assert len(recipes_with_one_food) == 15

    # Get all recipes with both foods
    recipes_with_both_foods = database.recipes.page_all(
        pagination_query, foods=[food.id for food in created_foods]
    ).items
    assert len(recipes_with_both_foods) == 10

    # Get all recipes with either foods
    recipes_with_either_food = database.recipes.page_all(
        pagination_query, foods=[food.id for food in created_foods], require_all_foods=False
    ).items

    assert len(recipes_with_either_food) == 20

    pagination_query = PaginationQuery(
        page=1,
        per_page=-1,
        order_by="random",
        pagination_seed=str(datetime.now(timezone.utc)),
        order_direction=OrderDirection.asc,
    )
    random_ordered = []
    for i in range(5):
        pagination_query.pagination_seed = str(datetime.now(timezone.utc))
        random_ordered.append(database.recipes.page_all(pagination_query, foods=[food_id]).items)
    assert len(random_ordered[0]) == 15
    assert not all(i == random_ordered[0] for i in random_ordered)


@pytest.mark.parametrize(
    "search, expected_names",
    [
        (random_string(), []),
        ("Steinbock", ["Steinbock Sloop"]),
        ("horns", ["Steinbock Sloop"]),
        ("moss", ["Fiddlehead Fern Stir Fry"]),
        ('"Animal Sloop"', ["Animal Sloop"]),
        ("animal-sloop", ["Animal Sloop"]),
        ("ratat", ["Rátàtôuile"]),
        ("delicious horns", ["Steinbock Sloop"]),
    ],
    ids=[
        "no_match",
        "search_by_title",
        "search_by_description",
        "search_by_ingredient",
        "literal_search",
        "special_character_removal",
        "normalization",
        "token_separation",
    ],
)
def test_basic_recipe_search(
    search: str,
    expected_names: list[str],
    database: AllRepositories,
    search_recipes: list[Recipe],  # required so database is populated
    unique_local_group_id: str,
):
    repo = database.recipes.by_group(unique_local_group_id)  # type: ignore
    pagination = PaginationQuery(page=1, per_page=-1, order_by="created_at", order_direction=OrderDirection.asc)
    results = repo.page_all(pagination, search=search).items

    if len(expected_names) == 0:
        assert len(results) == 0
    else:
        # if more results are returned, that's acceptable, as long as they are ranked correctly
        assert len(results) >= len(expected_names)
        for recipe, name in zip(results, expected_names, strict=False):
            assert recipe.name == name


def test_fuzzy_recipe_search(
    database: AllRepositories,
    search_recipes: list[Recipe],  # required so database is populated
    unique_local_group_id: str,
):
    # this only works on postgres
    if database.session.get_bind().name != "postgresql":
        return

    repo = database.recipes.by_group(unique_local_group_id)  # type: ignore
    pagination = PaginationQuery(page=1, per_page=-1, order_by="created_at", order_direction=OrderDirection.asc)
    results = repo.page_all(pagination, search="Steinbuck").items

    assert results and results[0].name == "Steinbock Sloop"


def test_random_order_recipe_search(
    database: AllRepositories,
    search_recipes: list[Recipe],  # required so database is populated
    unique_local_group_id: str,
):
    repo = database.recipes.by_group(unique_local_group_id)  # type: ignore
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
        random_ordered.append(repo.page_all(pagination, search="soup").items)
    assert not all(i == random_ordered[0] for i in random_ordered)


def test_order_by_rating(database: AllRepositories, user_tuple: tuple[TestUser, TestUser]):
    user_1, user_2 = user_tuple
    repo = database.recipes.by_group(UUID(user_1.group_id))

    recipes: list[Recipe] = []
    for i in range(3):
        slug = f"recipe-{i+1}-{random_string(5)}"
        recipes.append(
            database.recipes.create(
                Recipe(
                    user_id=user_1.user_id,
                    group_id=user_1.group_id,
                    name=slug,
                    slug=slug,
                )
            )
        )

    # set the rating for user_1 and confirm both users see the same ordering
    recipe_1, recipe_2, recipe_3 = recipes
    database.user_ratings.create(
        UserRatingCreate(
            user_id=user_1.user_id,
            recipe_id=recipe_1.id,
            rating=5,
        )
    )
    database.user_ratings.create(
        UserRatingCreate(
            user_id=user_1.user_id,
            recipe_id=recipe_2.id,
            rating=4,
        )
    )
    database.user_ratings.create(
        UserRatingCreate(
            user_id=user_1.user_id,
            recipe_id=recipe_3.id,
            rating=3,
        )
    )

    pq = PaginationQuery(page=1, per_page=-1, order_by="rating", order_direction=OrderDirection.desc)
    data_1 = repo.by_user(user_1.user_id).page_all(pq).items
    data_2 = repo.by_user(user_2.user_id).page_all(pq).items
    for data in [data_1, data_2]:
        assert len(data) == 3
        assert data[0].slug == recipe_1.slug  # global and user rating == 5
        assert data[1].slug == recipe_2.slug  # global and user rating == 4
        assert data[2].slug == recipe_3.slug  # global and user rating == 3

    pq = PaginationQuery(page=1, per_page=-1, order_by="rating", order_direction=OrderDirection.asc)
    data_1 = repo.by_user(user_1.user_id).page_all(pq).items
    data_2 = repo.by_user(user_2.user_id).page_all(pq).items
    for data in [data_1, data_2]:
        assert len(data) == 3
        assert data[0].slug == recipe_3.slug  # global and user rating == 3
        assert data[1].slug == recipe_2.slug  # global and user rating == 4
        assert data[2].slug == recipe_1.slug  # global and user rating == 5

    # set rating for one recipe for user_2 and confirm user_2 sees the correct order and user_1's order is unchanged
    database.user_ratings.create(
        UserRatingCreate(
            user_id=user_2.user_id,
            recipe_id=recipe_1.id,
            rating=3.5,
        )
    )

    pq = PaginationQuery(page=1, per_page=-1, order_by="rating", order_direction=OrderDirection.desc)
    data_1 = repo.by_user(user_1.user_id).page_all(pq).items
    data_2 = repo.by_user(user_2.user_id).page_all(pq).items

    assert len(data_1) == 3
    assert data_1[0].slug == recipe_1.slug  # user rating == 5
    assert data_1[1].slug == recipe_2.slug  # user rating == 4
    assert data_1[2].slug == recipe_3.slug  # user rating == 3

    assert len(data_2) == 3
    assert data_2[0].slug == recipe_2.slug  # global rating == 4
    assert data_2[1].slug == recipe_1.slug  # user rating == 3.5
    assert data_2[2].slug == recipe_3.slug  # user rating == 3

    pq = PaginationQuery(page=1, per_page=-1, order_by="rating", order_direction=OrderDirection.asc)
    data_1 = repo.by_user(user_1.user_id).page_all(pq).items
    data_2 = repo.by_user(user_2.user_id).page_all(pq).items

    assert len(data_1) == 3
    assert data_1[0].slug == recipe_3.slug  # global and user rating == 3
    assert data_1[1].slug == recipe_2.slug  # global and user rating == 4
    assert data_1[2].slug == recipe_1.slug  # global and user rating == 5

    assert len(data_2) == 3
    assert data_2[0].slug == recipe_3.slug  # user rating == 3
    assert data_2[1].slug == recipe_1.slug  # user rating == 3.5
    assert data_2[2].slug == recipe_2.slug  # global rating == 4

    # verify public users see only global ratings
    database.user_ratings.create(
        UserRatingCreate(
            user_id=user_2.user_id,
            recipe_id=recipe_2.id,
            rating=1,
        )
    )

    pq = PaginationQuery(page=1, per_page=-1, order_by="rating", order_direction=OrderDirection.desc)
    data = database.recipes.by_group(UUID(user_1.group_id)).page_all(pq).items

    assert len(data) == 3
    assert data[0].slug == recipe_1.slug  # global rating == 4.25 (avg of 5 and 3.5)
    assert data[1].slug == recipe_3.slug  # global rating == 3
    assert data[2].slug == recipe_2.slug  # global rating == 2.5 (avg of 4 and 1)

    pq = PaginationQuery(page=1, per_page=-1, order_by="rating", order_direction=OrderDirection.asc)
    data = database.recipes.by_group(UUID(user_1.group_id)).page_all(pq).items

    assert len(data) == 3
    assert data[0].slug == recipe_2.slug  # global rating == 2.5 (avg of 4 and 1)
    assert data[1].slug == recipe_3.slug  # global rating == 3
    assert data[2].slug == recipe_1.slug  # global rating == 4.25 (avg of 5 and 3.5)
