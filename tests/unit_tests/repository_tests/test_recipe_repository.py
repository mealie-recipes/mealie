from collections import Counter

from mealie.repos.repository_factory import AllRepositories
from mealie.repos.repository_recipes import RepositoryRecipes
from mealie.schema.recipe.recipe import Recipe, RecipeCategory
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_recipe_repo_get_by_categories_basic(database: AllRepositories, unique_user: TestUser):
    # Bootstrap the database with categories
    slug1, slug2, slug3 = [random_string(10) for _ in range(3)]

    categories = [
        RecipeCategory(name=slug1, slug=slug1),
        RecipeCategory(name=slug2, slug=slug2),
        RecipeCategory(name=slug3, slug=slug3),
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
        RecipeCategory(name=slug1, slug=slug1),
        RecipeCategory(name=slug2, slug=slug2),
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


def test_recipe_repo_get_random_by_categories(database: AllRepositories, unique_user: TestUser):
    # Setup Category
    category_slug = random_string(10)
    test_category = RecipeCategory(name=category_slug, slug=category_slug)
    category_model = database.categories.create(test_category)

    # Create 30 Recipes
    recipes = []

    for idx in range(30):
        category = [category_model] if idx % 2 == 0 else []

        recipe_model = database.recipes.create(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                recipe_category=category,
            ),
        )

        recipes.append(recipe_model)

    # Peform Random Recipe Query Multiple Times for Sudo Random Testing

    random_recipes = []

    for _ in range(10):
        repo: RepositoryRecipes = database.recipes.by_group(unique_user.group_id)
        recipe = repo.get_random_by_categories([category_model])[0]

        ids = [cat.id for cat in recipe.recipe_category]

        assert category_model.id in ids

        random_recipes.append(recipe)

    # Ensure that each recipe is unique within reason
    counts = Counter(x.id for x in random_recipes)

    for key, value in counts.items():
        assert value < 5

    # Cleanup

    for recipe in recipes:
        database.recipes.delete(recipe.slug)

    database.categories.delete(category_model.slug)
