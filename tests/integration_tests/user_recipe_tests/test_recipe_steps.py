import json
import random

from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_step import IngredientReferences
from tests.utils import jsonify, routes
from tests.utils.fixture_schemas import TestUser


def test_associate_ingredient_with_step(api_client: TestClient, unique_user: TestUser, random_recipe: Recipe):
    recipe: Recipe = random_recipe

    # Associate an ingredient with a step

    steps = {}  # key=step_id, value=ingredient_id

    for idx, step in enumerate(recipe.recipe_instructions):
        ingredients = random.choices(recipe.recipe_ingredient, k=2)

        step.ingredient_references = [
            IngredientReferences(reference_id=ingredient.reference_id) for ingredient in ingredients
        ]

        steps[idx] = [str(ingredient.reference_id) for ingredient in ingredients]

    response = api_client.put(
        routes.RoutesRecipe.item(recipe.slug),
        json=jsonify(recipe.dict()),
        headers=unique_user.token,
    )

    assert response.status_code == 200

    # Get Recipe and check that the ingredient is associated with the step

    response = api_client.get(routes.RoutesRecipe.item(recipe.slug), headers=unique_user.token)

    assert response.status_code == 200

    recipe = json.loads(response.text)

    for idx, step in enumerate(recipe.get("recipeInstructions")):
        all_refs = [ref["referenceId"] for ref in step.get("ingredientReferences")]

        assert len(all_refs) == 2

        print(steps)
        print(f"Step {idx}: {all_refs}")

        assert all(ref in steps[idx] for ref in all_refs)
