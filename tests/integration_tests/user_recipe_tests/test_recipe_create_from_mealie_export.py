import io
import json
import zipfile
from collections.abc import Callable
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from pytest import MonkeyPatch

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser
from tests.utils.helpers import parse_sse_events


def create_populated_recipe(api_client: TestClient, user: TestUser) -> dict:
    """Create a recipe that uses every part an export carries, and return it as the API serves it."""
    headers = user.token
    category = api_client.post(api_routes.organizers_categories, json={"name": random_string()}, headers=headers).json()
    tag = api_client.post(api_routes.organizers_tags, json={"name": random_string()}, headers=headers).json()
    tool = api_client.post(api_routes.organizers_tools, json={"name": random_string()}, headers=headers).json()
    food = api_client.post(api_routes.foods, json={"name": random_string()}, headers=headers).json()
    unit = api_client.post(api_routes.units, json={"name": random_string()}, headers=headers).json()

    slug = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=headers).json()
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=headers).json()

    reference_id = str(uuid4())
    note_reference_id = str(uuid4())
    recipe.update(
        {
            "description": "the description",
            "recipeYield": "4 servings",
            "recipeServings": 4,
            "orgURL": "https://example.com/original",
            "recipeCategory": [category],
            "tags": [tag],
            "tools": [tool],
            "nutrition": {"calories": "350", "proteinContent": "25"},
            "notes": [{"title": "Tip", "text": "Rest before serving.", "referenceId": note_reference_id}],
            "extras": {"my_key": "my_value"},
            "settings": {
                "public": False,
                "showNutrition": True,
                "showAssets": True,
                "landscapeView": True,
                "disableComments": True,
                "locked": False,
            },
            "recipeIngredient": [
                {
                    "referenceId": reference_id,
                    "title": "For the sauce",
                    "quantity": 2,
                    "unit": unit,
                    "food": food,
                    "note": "warmed",
                }
            ],
            "recipeInstructions": [
                {
                    "title": "Prep Work",
                    "summary": "Season the meat",
                    "text": "Season the **beef**.",
                    "ingredientReferences": [{"referenceId": reference_id}],
                    "noteReferences": [{"referenceId": note_reference_id}],
                }
            ],
        }
    )
    assert api_client.put(api_routes.recipes_slug(slug), json=recipe, headers=headers).status_code == 200
    return api_client.get(api_routes.recipes_slug(slug), headers=headers).json()


def snake_case_export(api_client: TestClient, user: TestUser, slug: str) -> str:
    """The JSON file inside the recipe's export zip."""
    export = api_client.get(api_routes.recipes_slug_exports(slug), params={"template_name": "zip"}, headers=user.token)
    assert export.status_code == 200
    with zipfile.ZipFile(io.BytesIO(export.content)) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".json"))
        return zf.read(name).decode()


def camel_case_export(api_client: TestClient, user: TestUser, slug: str) -> str:
    """What the recipe page's JSON editor shows: the recipe as the API serves it."""
    return api_client.get(api_routes.recipes_slug(slug), headers=user.token).text


EXPORTS: list[Callable[[TestClient, TestUser, str], str]] = [snake_case_export, camel_case_export]


def paste(
    api_client: TestClient, user: TestUser, data: str, include_tags: bool = True, include_categories: bool = True
) -> Response:
    return api_client.post(
        api_routes.recipes_create_html_or_json,
        json={"data": data, "include_tags": include_tags, "include_categories": include_categories},
        headers=user.token,
    )


@pytest.mark.parametrize("export", EXPORTS, ids=["snake_case", "camelCase"])
def test_paste_mealie_export_keeps_contents(
    api_client: TestClient, unique_user: TestUser, export: Callable[[TestClient, TestUser, str], str]
):
    original = create_populated_recipe(api_client, unique_user)

    r = paste(api_client, unique_user, export(api_client, unique_user, original["slug"]))
    assert r.status_code == 201, r.text

    imported = api_client.get(api_routes.recipes_slug(r.json()), headers=unique_user.token).json()
    assert imported["id"] != original["id"]
    for field in ["description", "recipeYield", "recipeServings", "orgURL", "extras", "settings", "nutrition"]:
        assert imported[field] == original[field], field

    assert [c["name"] for c in imported["recipeCategory"]] == [c["name"] for c in original["recipeCategory"]]
    assert [t["name"] for t in imported["tags"]] == [t["name"] for t in original["tags"]]
    assert [t["name"] for t in imported["tools"]] == [t["name"] for t in original["tools"]]
    assert [(n["title"], n["text"]) for n in imported["notes"]] == [("Tip", "Rest before serving.")]

    ingredient = imported["recipeIngredient"][0]
    assert ingredient["title"] == "For the sauce"
    assert ingredient["quantity"] == 2
    assert ingredient["unit"]["name"] == original["recipeIngredient"][0]["unit"]["name"]
    assert ingredient["food"]["name"] == original["recipeIngredient"][0]["food"]["name"]
    assert ingredient["note"] == "warmed"

    step = imported["recipeInstructions"][0]
    assert (step["title"], step["summary"], step["text"]) == ("Prep Work", "Season the meat", "Season the **beef**.")
    assert [ref["referenceId"] for ref in step["ingredientReferences"]] == [ingredient["referenceId"]]

    # the recipe the export came from is untouched
    still_there = api_client.get(api_routes.recipes_slug(original["slug"]), headers=unique_user.token)
    assert still_there.status_code == 200
    assert still_there.json()["id"] == original["id"]


def test_paste_mealie_export_honours_organizer_options(api_client: TestClient, unique_user: TestUser):
    original = create_populated_recipe(api_client, unique_user)

    r = paste(
        api_client,
        unique_user,
        camel_case_export(api_client, unique_user, original["slug"]),
        include_tags=False,
        include_categories=False,
    )
    assert r.status_code == 201, r.text

    imported = api_client.get(api_routes.recipes_slug(r.json()), headers=unique_user.token).json()
    assert imported["tags"] == []
    assert imported["recipeCategory"] == []
    # tools have no option on the import page, so they are always kept
    assert [t["name"] for t in imported["tools"]] == [t["name"] for t in original["tools"]]


def test_paste_mealie_export_drops_files_and_comments(api_client: TestClient, unique_user: TestUser):
    original = create_populated_recipe(api_client, unique_user)
    data = json.loads(camel_case_export(api_client, unique_user, original["slug"]))
    data["image"] = "abcd"
    data["assets"] = [{"name": "manual", "icon": "mdi-file", "fileName": "manual.pdf"}]
    # a hand-edited comment that would not validate on its own
    data["comments"] = [{"text": "looks great"}]

    r = paste(api_client, unique_user, json.dumps(data))
    assert r.status_code == 201, r.text

    imported = api_client.get(api_routes.recipes_slug(r.json()), headers=unique_user.token).json()
    assert imported["image"] is None
    assert imported["assets"] == []
    assert imported["comments"] == []


def test_paste_mealie_export_streams_done(api_client: TestClient, unique_user: TestUser):
    original = create_populated_recipe(api_client, unique_user)

    response = api_client.post(
        api_routes.recipes_create_html_or_json_stream,
        json={"data": camel_case_export(api_client, unique_user, original["slug"])},
        headers=unique_user.token,
    )
    assert response.status_code == 200

    events = parse_sse_events(response.text)
    done = [e for e in events if e["event"] == "done"]
    assert done
    imported = api_client.get(api_routes.recipes_slug(done[0]["data"]["slug"]), headers=unique_user.token)
    assert imported.status_code == 200


def test_paste_mealie_export_skips_the_scraper(api_client: TestClient, unique_user: TestUser, monkeypatch: MonkeyPatch):
    async def fail(*args, **kwargs):
        raise AssertionError("a Mealie export must not reach the web scraper")

    monkeypatch.setattr("mealie.routes.recipe.recipe_crud_routes.create_from_html", fail)
    original = create_populated_recipe(api_client, unique_user)

    r = paste(api_client, unique_user, snake_case_export(api_client, unique_user, original["slug"]))
    assert r.status_code == 201, r.text
