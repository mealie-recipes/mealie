"""Canonical app/DB coverage. Requires migration review before running conftest."""

import json
from io import BytesIO
from uuid import uuid4
from zipfile import ZipFile

import pytest

from mealie.schema.recipe import Recipe
from mealie.services.recipe.template_service import TemplateService
from tests.utils import api_routes


@pytest.mark.parametrize("clear_value", [None, 0])
def test_duration_persists_edits_clears_and_exports_for_zip_import(api_client, unique_user, tmp_path, clear_value):
    response = api_client.post(api_routes.recipes, json={"name": f"Duration {uuid4()}"}, headers=unique_user.token)
    assert response.status_code == 201
    slug = response.json()
    route = api_routes.recipes_slug(slug)
    recipe = api_client.get(route, headers=unique_user.token).json()
    recipe["recipeInstructions"] = [
        {"text": "Legacy, no explicit time"},
        {"text": "Explicitly unspecified", "durationSeconds": None},
        {"text": "Rest", "durationSeconds": 3661},
    ]
    assert api_client.put(route, json=recipe, headers=unique_user.token).status_code == 200
    reloaded = api_client.get(route, headers=unique_user.token).json()
    assert [step["durationSeconds"] for step in reloaded["recipeInstructions"]] == [None, None, 3661]

    # Fresh GET crosses the request-scoped session boundary, rather than reading a mock ORM object.
    reloaded["recipeInstructions"][2]["durationSeconds"] = 42
    assert api_client.put(route, json=reloaded, headers=unique_user.token).status_code == 200
    reloaded = api_client.get(route, headers=unique_user.token).json()
    assert reloaded["recipeInstructions"][2]["durationSeconds"] == 42
    exported = TemplateService(temp=tmp_path).render(Recipe.model_validate(reloaded), "raw")
    imported = json.loads(exported.read_text())
    assert [step["durationSeconds"] for step in imported["recipeInstructions"]] == [None, None, 42]
    imported["id"] = str(uuid4())
    imported["name"] = imported["slug"] = f"duration-import-{uuid4()}"
    for step in imported["recipeInstructions"]:
        step["id"] = str(uuid4())
    archive = BytesIO()
    with ZipFile(archive, "w") as output:
        output.writestr("recipe.json", json.dumps(imported))
    response = api_client.post(
        api_routes.recipes_create_zip, files={"archive": archive.getvalue()}, headers=unique_user.token
    )
    assert response.status_code == 201
    restored = api_client.get(api_routes.recipes_slug(imported["slug"]), headers=unique_user.token)
    assert restored.status_code == 200
    assert [step["durationSeconds"] for step in restored.json()["recipeInstructions"]] == [None, None, 42]

    reloaded["recipeInstructions"][2]["durationSeconds"] = clear_value
    assert api_client.put(route, json=reloaded, headers=unique_user.token).status_code == 200
    cleared = api_client.get(route, headers=unique_user.token).json()
    assert cleared["recipeInstructions"][2]["durationSeconds"] is None
    assert cleared["recipeInstructions"][2]["text"] == "Rest"


@pytest.mark.parametrize("number", ["1", "1.0", "1e0", "2147483647.0"])
def test_api_persists_whole_numeric_spellings(api_client, unique_user, random_recipe, number):
    route = api_routes.recipes_slug(random_recipe.slug)
    recipe = api_client.get(route, headers=unique_user.token).json()
    recipe["recipeInstructions"] = [{"text": "Exact seconds", "durationSeconds": "NUMERIC_PLACEHOLDER"}]
    body = json.dumps(recipe).replace('"NUMERIC_PLACEHOLDER"', number)
    response = api_client.put(route, content=body, headers={**unique_user.token, "Content-Type": "application/json"})
    assert response.status_code == 200
    restored = api_client.get(route, headers=unique_user.token).json()["recipeInstructions"][0]
    assert type(restored["durationSeconds"]) is int
    assert restored["durationSeconds"] == int(float(number))


@pytest.mark.parametrize("value", [True, False, "90", -1, 1.5, 2147483647.5, "", " ", 2147483648])
def test_api_rejects_invalid_duration_without_saving(api_client, unique_user, random_recipe, value):
    route = api_routes.recipes_slug(random_recipe.slug)
    before = api_client.get(route, headers=unique_user.token).json()
    payload = {**before, "recipeInstructions": [{"text": "Invalid", "durationSeconds": value}]}
    assert api_client.put(route, json=payload, headers=unique_user.token).status_code == 422
    after = api_client.get(route, headers=unique_user.token).json()
    assert after["recipeInstructions"] == before["recipeInstructions"]
