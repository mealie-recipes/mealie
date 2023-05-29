from datetime import datetime
from typing import cast

from mealie.repos.repository_factory import AllRepositories
from mealie.repos.repository_recipes import RepositoryRecipes
from mealie.schema.recipe import RecipeIngredient, SaveIngredientFood, RecipeStep
from mealie.schema.recipe.recipe import Recipe, RecipeCategory, RecipeSummary
from mealie.schema.recipe.recipe_category import CategoryOut, CategorySave, TagSave
from mealie.schema.recipe.recipe_tool import RecipeToolSave
from mealie.schema.response import OrderDirection, PaginationQuery
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


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
    repo: RepositoryRecipes = database.recipes.by_group(unique_user.group_id)  # type: ignore
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
        pagination_seed=str(datetime.now()),
        order_direction=OrderDirection.asc,
    )
    random_ordered = []
    for i in range(5):
        pagination_query.pagination_seed = str(datetime.now())
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
        pagination_seed=str(datetime.now()),
        order_direction=OrderDirection.asc,
    )
    random_ordered = []
    for i in range(5):
        pagination_query.pagination_seed = str(datetime.now())
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
        pagination_seed=str(datetime.now()),
        order_direction=OrderDirection.asc,
    )
    random_ordered = []
    for i in range(5):
        pagination_query.pagination_seed = str(datetime.now())
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
        pagination_seed=str(datetime.now()),
        order_direction=OrderDirection.asc,
    )
    random_ordered = []
    for i in range(5):
        pagination_query.pagination_seed = str(datetime.now())
        random_ordered.append(database.recipes.page_all(pagination_query, foods=[food_id]).items)
    assert len(random_ordered[0]) == 15
    assert not all(i == random_ordered[0] for i in random_ordered)


def test_recipe_repo_search(database: AllRepositories, unique_user: TestUser):
    recipes = [
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name="Steinbock Sloop",
            description=f"My favorite horns are delicious",
            recipe_ingredient=[
                RecipeIngredient(note="alpine animal"),
            ],
        ),
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name="Fiddlehead Fern Stir Fry",
            recipe_ingredient=[
                RecipeIngredient(note="moss"),
            ],
        ),
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name="Animal Sloop",
        ),
        # Test diacritics
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name="Rátàtôuile",
        ),
        # Add a bunch of recipes for stable randomization
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=f"{random_string(10)} soup",
        ),
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=f"{random_string(10)} soup",
        ),
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=f"{random_string(10)} soup",
        ),
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=f"{random_string(10)} soup",
        ),
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=f"{random_string(10)} soup",
        ),
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=f"{random_string(10)} soup",
        ),
    ]

    for recipe in recipes:
        database.recipes.create(recipe)

    pagination_query = PaginationQuery(page=1, per_page=-1, order_by="created_at", order_direction=OrderDirection.asc)

    # No hits
    empty_result = database.recipes.page_all(pagination_query, search=random_string(10)).items
    assert len(empty_result) == 0

    # Search by title
    title_result = database.recipes.page_all(pagination_query, search="Steinbock").items
    assert len(title_result) == 1
    assert title_result[0].name == "Steinbock Sloop"

    # Search by description
    description_result = database.recipes.page_all(pagination_query, search="horns").items
    assert len(description_result) == 1
    assert description_result[0].name == "Steinbock Sloop"

    # Search by ingredient
    ingredient_result = database.recipes.page_all(pagination_query, search="moss").items
    assert len(ingredient_result) == 1
    assert ingredient_result[0].name == "Fiddlehead Fern Stir Fry"

    # Make sure title matches are ordered in front
    ordered_result = database.recipes.page_all(pagination_query, search="animal sloop").items
    assert len(ordered_result) == 2
    assert ordered_result[0].name == "Animal Sloop"
    assert ordered_result[1].name == "Steinbock Sloop"

    # Test literal search
    literal_result = database.recipes.page_all(pagination_query, search='"Animal Sloop"').items
    assert len(literal_result) == 1
    assert literal_result[0].name == "Animal Sloop"

    # Test special character removal from non-literal searches
    character_result = database.recipes.page_all(pagination_query, search="animal-sloop").items
    assert len(character_result) == 2
    assert character_result[0].name == "Animal Sloop"
    assert character_result[1].name == "Steinbock Sloop"

    # Test string normalization
    normalized_result = database.recipes.page_all(pagination_query, search="ratat").items
    print([r.name for r in normalized_result])
    assert len(normalized_result) == 1
    assert normalized_result[0].name == "Rátàtôuile"

    # Test token separation
    token_result = database.recipes.page_all(pagination_query, search="delicious horns").items
    assert len(token_result) == 1
    assert token_result[0].name == "Steinbock Sloop"

    # Test fuzzy search
    if database.session.get_bind().name == "postgresql":
        fuzzy_result = database.recipes.page_all(pagination_query, search="Steinbuck").items
        assert len(fuzzy_result) == 1
        assert fuzzy_result[0].name == "Steinbock Sloop"

    # Test random ordering with search
    pagination_query = PaginationQuery(
        page=1,
        per_page=-1,
        order_by="random",
        pagination_seed=str(datetime.now()),
        order_direction=OrderDirection.asc,
    )
    random_ordered = []
    for i in range(5):
        pagination_query.pagination_seed = str(datetime.now())
        random_ordered.append(database.recipes.page_all(pagination_query, search="soup").items)
    assert not all(i == random_ordered[0] for i in random_ordered)
