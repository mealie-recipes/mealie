from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe import RecipeDraft
from mealie.schema.recipe.recipe_ingredient import IngredientFoodSave, IngredientUnitSave
from mealie.schema.recipe.recipe_organizers import CategorySave, TagSave, ToolSave
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

SAVE_SCHEMAS = {"tags": TagSave, "categories": CategorySave, "tools": ToolSave}

# repo name, recipe attribute (snake_case), recipe field in the API payload
ORGANIZERS = [
    ("tags", "tags", "tags"),
    ("categories", "recipe_category", "recipeCategory"),
    ("tools", "tools", "tools"),
]
ORGANIZER_IDS = [o[0] for o in ORGANIZERS]


def _create_organizer(user: TestUser, repo_name: str) -> dict:
    repo = getattr(user.repos, repo_name)
    organizer = repo.create(SAVE_SCHEMAS[repo_name](name=random_string(), group_id=user.group_id))
    return {"id": str(organizer.id), "name": organizer.name, "slug": organizer.slug}


def _assert_untouched(owner: TestUser, repo_name: str, organizer: dict) -> None:
    after = getattr(owner.repos, repo_name).get_one(organizer["id"])
    assert after is not None
    assert str(after.group_id) == owner.group_id
    assert after.name == organizer["name"]
    assert after.slug == organizer["slug"]


@pytest.mark.parametrize("by_id", [True, False], ids=["by_id", "by_slug"])
@pytest.mark.parametrize("repo_name, attribute, _", ORGANIZERS, ids=ORGANIZER_IDS)
def test_recipe_create_cannot_adopt_organizer_from_another_group(
    repo_name: str, attribute: str, _: str, by_id: bool, unique_user: TestUser, g2_user: TestUser
):
    victim = _create_organizer(g2_user, repo_name)
    reference = {
        # the schema requires an id even when the client only knows the slug
        "id": victim["id"] if by_id else str(uuid4()),
        "name": victim["name"],
        "slug": victim["slug"],
        "group_id": unique_user.group_id,
    }

    created = unique_user.repos.recipes.create(
        RecipeDraft(
            user_id=unique_user.user_id, group_id=unique_user.group_id, name=random_string(), **{attribute: [reference]}
        )
    )

    _assert_untouched(g2_user, repo_name, victim)
    assert victim["id"] not in [str(item.id) for item in getattr(created, attribute)]


@pytest.mark.parametrize("by_id", [True, False], ids=["by_id", "by_slug"])
@pytest.mark.parametrize("repo_name, _, field", ORGANIZERS, ids=ORGANIZER_IDS)
def test_recipe_update_cannot_adopt_organizer_from_another_group(
    repo_name: str, _: str, field: str, by_id: bool, api_client: TestClient, unique_user: TestUser, g2_user: TestUser
):
    victim = _create_organizer(g2_user, repo_name)

    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=unique_user.token)
    assert response.status_code == 201
    slug = response.json()

    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    reference = {"name": victim["name"], "slug": victim["slug"]}
    if by_id:
        reference["id"] = victim["id"]
    recipe[field] = [reference]
    response = api_client.put(api_routes.recipes_slug(slug), json=recipe, headers=unique_user.token)
    assert response.status_code == 200

    assert victim["id"] not in [item["id"] for item in response.json()[field]]
    _assert_untouched(g2_user, repo_name, victim)


@pytest.mark.parametrize(
    "repo_name, schema, field",
    [("ingredient_foods", IngredientFoodSave, "food"), ("ingredient_units", IngredientUnitSave, "unit")],
    ids=["foods", "units"],
)
def test_recipe_ingredient_cannot_link_food_or_unit_from_another_group(
    repo_name: str,
    schema: type[IngredientFoodSave] | type[IngredientUnitSave],
    field: str,
    api_client: TestClient,
    unique_user: TestUser,
    g2_user: TestUser,
):
    victim = getattr(g2_user.repos, repo_name).create(schema(name=random_string(), group_id=g2_user.group_id))

    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=unique_user.token)
    assert response.status_code == 201
    slug = response.json()

    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    recipe["recipeIngredient"] = [
        {"quantity": 1, "note": "", "referenceId": str(uuid4()), field: {"id": str(victim.id), "name": victim.name}}
    ]
    response = api_client.put(api_routes.recipes_slug(slug), json=recipe, headers=unique_user.token)
    assert response.status_code == 200

    linked = response.json()["recipeIngredient"][0][field]
    assert linked is None or linked["id"] != str(victim.id)

    # g2_user's repo is group-scoped, so finding the row proves it is still in group 2.
    after = getattr(g2_user.repos, repo_name).get_one(victim.id)
    assert after is not None
    assert after.name == victim.name
