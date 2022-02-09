from mealie.repos.repository_factory import AllRepositories
from mealie.repos.repository_recipes import RepositoryRecipes
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_category import CategorySave
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_recipe_repo_get_by_categories_basic(database: AllRepositories, unique_user: TestUser):
    # Bootstrap the database with categories
    slug1, slug2, slug3 = [random_string(10) for _ in range(3)]

    categories = [
        CategorySave(group_id=unique_user.group_id, name=slug1, slug=slug1),
        CategorySave(group_id=unique_user.group_id, name=slug2, slug=slug2),
        CategorySave(group_id=unique_user.group_id, name=slug3, slug=slug3),
    ]

    created_categories = []

    for category in categories:
        model = database.categories.create(category)
        created_categories.append(model)

    # Bootstrap the database with recipes
    recipes = []

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
        models = database.recipes.create(recipe)
        created_recipes.append(models)

    # Get all recipes by category

    for category in created_categories:
        repo: RepositoryRecipes = database.recipes.by_group(unique_user.group_id)
        recipes = repo.get_by_categories([category])

        assert len(recipes) == 5

        for recipe in recipes:
            found_cat = recipe.recipe_category[0]

            assert found_cat.name == category.name
            assert found_cat.slug == category.slug
            assert found_cat.id == category.id


def test_recipe_repo_get_by_categories_multi(database: AllRepositories, unique_user: TestUser):
    slug1, slug2 = [random_string(10) for _ in range(2)]

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
    repo: RepositoryRecipes = database.recipes.by_group(unique_user.group_id)
    by_category = repo.get_by_categories(created_categories)

    assert len(by_category) == 10

    for recipe in by_category:
        for category in recipe.recipe_category:
            assert category.id in known_category_ids
