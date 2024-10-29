import inspect
import json
import os
import random
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from httpx import Response
from pytest import MonkeyPatch
from recipe_scrapers._abstract import AbstractScraper
from recipe_scrapers._schemaorg import SchemaOrg
from recipe_scrapers.plugins import SchemaOrgFillPlugin
from slugify import slugify

from mealie.pkgs.safehttp.transport import AsyncSafeTransport
from mealie.schema.cookbook.cookbook import SaveCookBook
from mealie.schema.recipe.recipe import Recipe, RecipeCategory, RecipeSummary, RecipeTag
from mealie.schema.recipe.recipe_category import CategorySave, TagSave
from mealie.schema.recipe.recipe_notes import RecipeNote
from mealie.schema.recipe.recipe_tool import RecipeToolSave
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.scraper.recipe_scraper import DEFAULT_SCRAPER_STRATEGIES
from tests import utils
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser
from tests.utils.recipe_data import get_recipe_test_cases

recipe_test_data = get_recipe_test_cases()


@pytest.fixture(scope="module")
def tempdir() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as td:
        yield td


def zip_recipe(tempdir: str, recipe: RecipeSummary) -> dict:
    data_file = tempfile.NamedTemporaryFile(mode="w+", dir=tempdir, suffix=".json", delete=False)
    json.dump(json.loads(recipe.model_dump_json()), data_file)
    data_file.flush()

    zip_file = shutil.make_archive(os.path.join(tempdir, "zipfile"), "zip")
    with ZipFile(zip_file, "w") as zf:
        zf.write(data_file.name)

    return {"archive": Path(zip_file).read_bytes()}


def get_init(html_path: Path):
    """
    Override the init method of the abstract scraper to return a bootstrapped init function that
    serves the html from the given path instead of calling the url.
    """

    def init_override(
        self,
        url,
        proxies: str | None = None,
        timeout: float | tuple | None = None,
        wild_mode: bool | None = False,
        **_,
    ):
        page_data = html_path.read_bytes()
        url = "https://test.example.com/"

        self.wild_mode = wild_mode
        self.soup = BeautifulSoup(page_data, "html.parser")
        self.url = url
        self.schema = SchemaOrg(page_data)

        # attach the SchemaOrgFill plugin
        if not hasattr(self.__class__, "plugins_initialized"):
            for name, _ in inspect.getmembers(self, inspect.ismethod):  # type: ignore
                current_method = getattr(self.__class__, name)
                current_method = SchemaOrgFillPlugin.run(current_method)
                setattr(self.__class__, name, current_method)
            self.__class__.plugins_initialized = True

    return init_override


def open_graph_override(html: str):
    async def get_html(self, url: str) -> str:
        return html

    return get_html


def test_create_by_url(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: MonkeyPatch,
):
    for recipe_data in recipe_test_data:
        # Override init function for AbstractScraper to use the test html instead of calling the url
        monkeypatch.setattr(
            AbstractScraper,
            "__init__",
            get_init(recipe_data.html_file),
        )
        # Override the get_html method of the RecipeScraperOpenGraph to return the test html
        for scraper_cls in DEFAULT_SCRAPER_STRATEGIES:
            monkeypatch.setattr(
                scraper_cls,
                "get_html",
                open_graph_override(recipe_data.html_file.read_text()),
            )

        # Skip AsyncSafeTransport requests
        async def return_empty_response(*args, **kwargs):
            return Response(200, content=b"")

        monkeypatch.setattr(
            AsyncSafeTransport,
            "handle_async_request",
            return_empty_response,
        )
        # Skip image downloader
        monkeypatch.setattr(
            RecipeDataService,
            "scrape_image",
            lambda *_: "TEST_IMAGE",
        )

        api_client.delete(api_routes.recipes_slug(recipe_data.expected_slug), headers=unique_user.token)

        response = api_client.post(
            api_routes.recipes_create_url,
            json={"url": recipe_data.url, "include_tags": recipe_data.include_tags},
            headers=unique_user.token,
        )

        assert response.status_code == 201
        assert json.loads(response.text) == recipe_data.expected_slug

        recipe = api_client.get(api_routes.recipes_slug(recipe_data.expected_slug), headers=unique_user.token)

        assert recipe.status_code == 200

        recipe_dict: dict = json.loads(recipe.text)

        assert recipe_dict["slug"] == recipe_data.expected_slug
        assert len(recipe_dict["recipeInstructions"]) == recipe_data.num_steps
        assert len(recipe_dict["recipeIngredient"]) == recipe_data.num_ingredients

        if not recipe_data.include_tags:
            return

        expected_tags = recipe_data.expected_tags or set()
        assert len(recipe_dict["tags"]) == len(expected_tags)

        for tag in recipe_dict["tags"]:
            assert tag["name"] in expected_tags


@pytest.mark.parametrize("use_json", [True, False])
def test_create_by_html_or_json(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: MonkeyPatch,
    use_json: bool,
):
    # Skip image downloader
    monkeypatch.setattr(
        RecipeDataService,
        "scrape_image",
        lambda *_: "TEST_IMAGE",
    )

    recipe_data = recipe_test_data[0]
    api_client.delete(api_routes.recipes_slug(recipe_data.expected_slug), headers=unique_user.token)

    data = recipe_data.html_file.read_text()
    if use_json:
        soup = BeautifulSoup(data, "lxml")
        ld_json_data = soup.find("script", type="application/ld+json")
        if ld_json_data:
            data = json.dumps(json.loads(ld_json_data.string))
        else:
            data = "{}"

    response = api_client.post(
        api_routes.recipes_create_html_or_json,
        json={"data": data, "include_tags": recipe_data.include_tags},
        headers=unique_user.token,
    )

    assert response.status_code == 201
    assert json.loads(response.text) == recipe_data.expected_slug

    recipe = api_client.get(api_routes.recipes_slug(recipe_data.expected_slug), headers=unique_user.token)

    assert recipe.status_code == 200

    recipe_dict: dict = json.loads(recipe.text)

    assert recipe_dict["slug"] == recipe_data.expected_slug
    assert len(recipe_dict["recipeInstructions"]) == recipe_data.num_steps
    assert len(recipe_dict["recipeIngredient"]) == recipe_data.num_ingredients

    if not recipe_data.include_tags:
        return

    expected_tags = recipe_data.expected_tags or set()
    assert len(recipe_dict["tags"]) == len(expected_tags)

    for tag in recipe_dict["tags"]:
        assert tag["name"] in expected_tags


def test_create_recipe_from_zip(api_client: TestClient, unique_user: TestUser, tempdir: str):
    database = unique_user.repos
    recipe_name = random_string()
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=unique_user.user_id,
        group_id=unique_user.group_id,
        name=recipe_name,
        slug=recipe_name,
    )

    r = api_client.post(api_routes.recipes_create_zip, files=zip_recipe(tempdir, recipe), headers=unique_user.token)
    assert r.status_code == 201

    fetched_recipe = database.recipes.get_by_slug(unique_user.group_id, recipe.slug)
    assert fetched_recipe


def test_create_recipe_from_zip_invalid_group(api_client: TestClient, unique_user: TestUser, tempdir: str):
    database = unique_user.repos
    recipe_name = random_string()
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=unique_user.user_id,
        group_id=uuid4(),
        name=recipe_name,
        slug=recipe_name,
    )

    r = api_client.post(api_routes.recipes_create_zip, files=zip_recipe(tempdir, recipe), headers=unique_user.token)
    assert r.status_code == 201

    fetched_recipe = database.recipes.get_by_slug(unique_user.group_id, recipe.slug)
    assert fetched_recipe

    # the group should always be set to the current user's group
    assert str(fetched_recipe.group_id) == str(unique_user.group_id)


def test_create_recipe_from_zip_invalid_user(api_client: TestClient, unique_user: TestUser, tempdir: str):
    database = unique_user.repos
    recipe_name = random_string()
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=uuid4(),
        group_id=unique_user.group_id,
        name=recipe_name,
        slug=recipe_name,
    )

    r = api_client.post(api_routes.recipes_create_zip, files=zip_recipe(tempdir, recipe), headers=unique_user.token)
    assert r.status_code == 201

    fetched_recipe = database.recipes.get_by_slug(unique_user.group_id, recipe.slug)
    assert fetched_recipe

    # invalid users should default to the current user
    assert str(fetched_recipe.user_id) == str(unique_user.user_id)


def test_create_recipe_from_zip_existing_category(api_client: TestClient, unique_user: TestUser, tempdir: str):
    database = unique_user.repos
    categories = database.categories.create_many(
        [{"name": random_string(), "group_id": unique_user.group_id} for _ in range(random_int(5, 10))]
    )
    category = random.choice(categories)

    recipe_name = random_string()
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=unique_user.user_id,
        group_id=unique_user.group_id,
        name=recipe_name,
        slug=recipe_name,
        recipe_category=[category],
    )

    r = api_client.post(api_routes.recipes_create_zip, files=zip_recipe(tempdir, recipe), headers=unique_user.token)
    assert r.status_code == 201

    fetched_recipe = database.recipes.get_by_slug(unique_user.group_id, recipe.slug)
    assert fetched_recipe
    assert fetched_recipe.recipe_category
    assert len(fetched_recipe.recipe_category) == 1
    assert str(fetched_recipe.recipe_category[0].id) == str(category.id)


def test_create_recipe_from_zip_existing_tag(api_client: TestClient, unique_user: TestUser, tempdir: str):
    database = unique_user.repos
    tags = database.tags.create_many(
        [{"name": random_string(), "group_id": unique_user.group_id} for _ in range(random_int(5, 10))]
    )
    tag = random.choice(tags)

    recipe_name = random_string()
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=unique_user.user_id,
        group_id=unique_user.group_id,
        name=recipe_name,
        slug=recipe_name,
        tags=[tag],
    )

    r = api_client.post(api_routes.recipes_create_zip, files=zip_recipe(tempdir, recipe), headers=unique_user.token)
    assert r.status_code == 201

    fetched_recipe = database.recipes.get_by_slug(unique_user.group_id, recipe.slug)
    assert fetched_recipe
    assert fetched_recipe.tags
    assert len(fetched_recipe.tags) == 1
    assert str(fetched_recipe.tags[0].id) == str(tag.id)


def test_create_recipe_from_zip_existing_category_wrong_ids(
    api_client: TestClient, unique_user: TestUser, tempdir: str
):
    database = unique_user.repos
    categories = database.categories.create_many(
        [{"name": random_string(), "group_id": unique_user.group_id} for _ in range(random_int(5, 10))]
    )
    category = random.choice(categories)
    invalid_category = RecipeCategory(id=uuid4(), name=category.name, slug=category.slug)

    recipe_name = random_string()
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=unique_user.user_id,
        group_id=unique_user.group_id,
        name=recipe_name,
        slug=recipe_name,
        recipe_category=[invalid_category],
    )

    r = api_client.post(api_routes.recipes_create_zip, files=zip_recipe(tempdir, recipe), headers=unique_user.token)
    assert r.status_code == 201

    fetched_recipe = database.recipes.get_by_slug(unique_user.group_id, recipe.slug)
    assert fetched_recipe
    assert fetched_recipe.recipe_category
    assert len(fetched_recipe.recipe_category) == 1
    assert str(fetched_recipe.recipe_category[0].id) == str(category.id)


def test_create_recipe_from_zip_existing_tag_wrong_ids(api_client: TestClient, unique_user: TestUser, tempdir: str):
    database = unique_user.repos
    tags = database.tags.create_many(
        [{"name": random_string(), "group_id": unique_user.group_id} for _ in range(random_int(5, 10))]
    )
    tag = random.choice(tags)
    invalid_tag = RecipeTag(id=uuid4(), name=tag.name, slug=tag.slug)

    recipe_name = random_string()
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=unique_user.user_id,
        group_id=unique_user.group_id,
        name=recipe_name,
        slug=recipe_name,
        tags=[invalid_tag],
    )

    r = api_client.post(api_routes.recipes_create_zip, files=zip_recipe(tempdir, recipe), headers=unique_user.token)
    assert r.status_code == 201

    fetched_recipe = database.recipes.get_by_slug(unique_user.group_id, recipe.slug)
    assert fetched_recipe
    assert fetched_recipe.tags
    assert len(fetched_recipe.tags) == 1
    assert str(fetched_recipe.tags[0].id) == str(tag.id)


def test_create_recipe_from_zip_invalid_category(api_client: TestClient, unique_user: TestUser, tempdir: str):
    database = unique_user.repos
    invalid_name = random_string()
    invalid_category = RecipeCategory(id=uuid4(), name=invalid_name, slug=invalid_name)

    recipe_name = random_string()
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=unique_user.user_id,
        group_id=unique_user.group_id,
        name=recipe_name,
        slug=recipe_name,
        recipe_category=[invalid_category],
    )

    r = api_client.post(api_routes.recipes_create_zip, files=zip_recipe(tempdir, recipe), headers=unique_user.token)
    assert r.status_code == 201

    fetched_recipe = database.recipes.get_by_slug(unique_user.group_id, recipe.slug)
    assert fetched_recipe
    assert fetched_recipe.recipe_category
    assert len(fetched_recipe.recipe_category) == 1

    # a new category should be created
    assert fetched_recipe.recipe_category[0].name == invalid_name
    assert fetched_recipe.recipe_category[0].slug == invalid_name


def test_create_recipe_from_zip_invalid_tag(api_client: TestClient, unique_user: TestUser, tempdir: str):
    database = unique_user.repos
    invalid_name = random_string()
    invalid_tag = RecipeTag(id=uuid4(), name=invalid_name, slug=invalid_name)

    recipe_name = random_string()
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=unique_user.user_id,
        group_id=unique_user.group_id,
        name=recipe_name,
        slug=recipe_name,
        tags=[invalid_tag],
    )

    r = api_client.post(api_routes.recipes_create_zip, files=zip_recipe(tempdir, recipe), headers=unique_user.token)
    assert r.status_code == 201

    fetched_recipe = database.recipes.get_by_slug(unique_user.group_id, recipe.slug)
    assert fetched_recipe
    assert fetched_recipe.tags
    assert len(fetched_recipe.tags) == 1

    # a new tag should be created
    assert fetched_recipe.tags[0].name == invalid_name
    assert fetched_recipe.tags[0].slug == invalid_name


def test_read_update(
    api_client: TestClient,
    unique_user: TestUser,
    recipe_categories: list[RecipeCategory],
):
    recipe_data = recipe_test_data[0]
    recipe_url = api_routes.recipes_slug(recipe_data.expected_slug)
    response = api_client.get(recipe_url, headers=unique_user.token)
    assert response.status_code == 200

    recipe = json.loads(response.text)

    test_notes = [
        {"title": "My Test Title1", "text": "My Test Text1"},
        {"title": "My Test Title2", "text": "My Test Text2"},
    ]

    recipe["notes"] = test_notes

    recipe["recipeCategory"] = [x.model_dump() for x in recipe_categories]

    response = api_client.put(recipe_url, json=utils.jsonify(recipe), headers=unique_user.token)

    assert response.status_code == 200
    assert json.loads(response.text).get("slug") == recipe_data.expected_slug

    response = api_client.get(recipe_url, headers=unique_user.token)
    assert response.status_code == 200
    recipe = json.loads(response.text)

    assert recipe["notes"] == test_notes

    assert len(recipe["recipeCategory"]) == len(recipe_categories)

    test_name = [x.name for x in recipe_categories]
    for cats in zip(recipe["recipeCategory"], recipe_categories, strict=False):
        assert cats[0]["name"] in test_name


@pytest.mark.parametrize("use_patch", [True, False])
def test_update_many(api_client: TestClient, unique_user: TestUser, use_patch: bool):
    recipe_slugs = [random_string() for _ in range(3)]
    for slug in recipe_slugs:
        api_client.post(api_routes.recipes, json={"name": slug}, headers=unique_user.token)

    recipes_data: list[dict] = [
        json.loads(api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).text)
        for slug in recipe_slugs
    ]

    new_slug_by_id = {r["id"]: random_string() for r in recipes_data}
    for recipe_data in recipes_data:
        recipe_data["name"] = new_slug_by_id[recipe_data["id"]]
        recipe_data["slug"] = new_slug_by_id[recipe_data["id"]]

    if use_patch:
        api_client_func = api_client.patch
    else:
        api_client_func = api_client.put
    response = api_client_func(api_routes.recipes, json=recipes_data, headers=unique_user.token)
    assert response.status_code == 200
    for updated_recipe_data in response.json():
        assert updated_recipe_data["slug"] == new_slug_by_id[updated_recipe_data["id"]]
        get_response = api_client.get(api_routes.recipes_slug(updated_recipe_data["slug"]), headers=unique_user.token)
        assert get_response.status_code == 200
        assert get_response.json()["slug"] == updated_recipe_data["slug"]


def test_duplicate(api_client: TestClient, unique_user: TestUser):
    recipe_data = recipe_test_data[0]

    # Initial get of the original recipe
    original_recipe_url = api_routes.recipes_slug(recipe_data.expected_slug)
    response = api_client.get(original_recipe_url, headers=unique_user.token)
    assert response.status_code == 200
    initial_recipe = json.loads(response.text)

    # Duplicate the recipe
    recipe_duplicate_url = api_routes.recipes_slug_duplicate(recipe_data.expected_slug)
    response = api_client.post(
        recipe_duplicate_url,
        headers=unique_user.token,
        json={
            "name": "Test Duplicate",
        },
    )
    assert response.status_code == 201

    duplicate_recipe = json.loads(response.text)
    assert duplicate_recipe["id"] != initial_recipe["id"]
    assert duplicate_recipe["slug"].startswith("test-duplicate")
    assert duplicate_recipe["name"].startswith("Test Duplicate")

    # Image should be copied (if it exists)
    assert (
        duplicate_recipe["image"] is None
        and initial_recipe["image"] is None
        or duplicate_recipe["image"] != initial_recipe["image"]
    )

    # Number of steps should be the same, but the text may have changed (link replacements)
    assert len(duplicate_recipe["recipeInstructions"]) == len(initial_recipe["recipeInstructions"])

    # Ingredients should have the same texts, but different ids
    assert duplicate_recipe["recipeIngredient"] != initial_recipe["recipeIngredient"]
    assert [i["note"] for i in duplicate_recipe["recipeIngredient"]] == [
        i["note"] for i in initial_recipe["recipeIngredient"]
    ]

    previous_categories = initial_recipe["recipeCategory"]
    assert duplicate_recipe["recipeCategory"] == previous_categories

    # Edit the duplicated recipe to make sure it doesn't affect the original
    dup_notes = duplicate_recipe["notes"] or []
    dup_notes.append({"title": "Test", "text": "Test"})
    duplicate_recipe["notes"] = dup_notes
    duplicate_recipe["recipeIngredient"][0]["note"] = "Different Ingredient"
    new_recipe_url = api_routes.recipes_slug(duplicate_recipe.get("slug"))
    response = api_client.put(new_recipe_url, json=duplicate_recipe, headers=unique_user.token)
    assert response.status_code == 200
    edited_recipe = json.loads(response.text)

    # reload original
    response = api_client.get(original_recipe_url, headers=unique_user.token)
    assert response.status_code == 200
    original_recipe = json.loads(response.text)

    assert edited_recipe["notes"] == dup_notes
    assert original_recipe.get("notes") != edited_recipe.get("notes")
    assert original_recipe.get("recipeCategory") == previous_categories

    # Make sure ingredient edits don't affect the original
    original_ingredients = original_recipe.get("recipeIngredient")
    edited_ingredients = edited_recipe.get("recipeIngredient")

    assert len(original_ingredients) == len(edited_ingredients)

    assert original_ingredients[0]["note"] != edited_ingredients[0]["note"]
    assert edited_ingredients[0]["note"] == "Different Ingredient"
    assert original_ingredients[0]["referenceId"] != edited_ingredients[1]["referenceId"]

    for i in range(1, len(original_ingredients)):
        assert original_ingredients[i]["referenceId"] != edited_ingredients[i]["referenceId"]

        def copy_info(ing):
            return {k: v for k, v in ing.items() if k != "referenceId"}

        assert copy_info(original_ingredients[i]) == copy_info(edited_ingredients[i])


# This needs to happen after test_duplicate,
# otherwise that one will run into problems with comparing the instruction/ingredient lists
def test_update_with_empty_relationship(
    api_client: TestClient,
    unique_user: TestUser,
):
    recipe_data = recipe_test_data[0]
    recipe_url = api_routes.recipes_slug(recipe_data.expected_slug)
    response = api_client.get(recipe_url, headers=unique_user.token)
    assert response.status_code == 200

    recipe = json.loads(response.text)

    recipe["recipeInstructions"] = []
    recipe["recipeIngredient"] = []

    response = api_client.put(recipe_url, json=utils.jsonify(recipe), headers=unique_user.token)

    assert response.status_code == 200
    assert json.loads(response.text).get("slug") == recipe_data.expected_slug

    response = api_client.get(recipe_url, headers=unique_user.token)
    assert response.status_code == 200
    recipe = json.loads(response.text)

    assert recipe["recipeInstructions"] == []
    assert recipe["recipeIngredient"] == []


def test_rename(api_client: TestClient, unique_user: TestUser):
    recipe_data = recipe_test_data[0]
    recipe_url = api_routes.recipes_slug(recipe_data.expected_slug)
    response = api_client.get(recipe_url, headers=unique_user.token)
    assert response.status_code == 200

    recipe = json.loads(response.text)
    new_name = recipe.get("name") + "-rename"
    new_slug = slugify(new_name)
    recipe["name"] = new_name

    response = api_client.put(recipe_url, json=recipe, headers=unique_user.token)

    assert response.status_code == 200
    assert json.loads(response.text).get("slug") == new_slug

    recipe_data.expected_slug = new_slug


def test_remove_notes(api_client: TestClient, unique_user: TestUser):
    # create recipe
    recipe_create_url = api_routes.recipes
    recipe_create_data = {"name": random_string()}
    response = api_client.post(recipe_create_url, headers=unique_user.token, json=recipe_create_data)
    assert response.status_code == 201
    recipe_slug: str = response.json()

    # get recipe and add a note
    recipe_url = api_routes.recipes_slug(recipe_slug)
    response = api_client.get(recipe_url, headers=unique_user.token)
    assert response.status_code == 200

    recipe = json.loads(response.text)
    recipe["notes"] = [RecipeNote(title=random_string(), text=random_string()).model_dump()]
    response = api_client.put(recipe_url, json=recipe, headers=unique_user.token)
    assert response.status_code == 200

    # get recipe and remove the note
    response = api_client.get(recipe_url, headers=unique_user.token)
    assert response.status_code == 200

    recipe = json.loads(response.text)
    assert len(recipe.get("notes", [])) == 1
    recipe["notes"] = []
    response = api_client.put(recipe_url, json=recipe, headers=unique_user.token)
    assert response.status_code == 200

    # verify the note is removed
    response = api_client.get(recipe_url, headers=unique_user.token)
    assert response.status_code == 200

    recipe = json.loads(response.text)
    assert len(recipe.get("notes", [])) == 0


def test_delete(api_client: TestClient, unique_user: TestUser):
    recipe_data = recipe_test_data[0]
    response = api_client.delete(api_routes.recipes_slug(recipe_data.expected_slug), headers=unique_user.token)
    assert response.status_code == 200


def test_recipe_crud_404(api_client: TestClient, unique_user: TestUser):
    response = api_client.put(api_routes.recipes_slug("test"), json={"test": "stest"}, headers=unique_user.token)
    assert response.status_code == 404

    response = api_client.get(api_routes.recipes_slug("test"), headers=unique_user.token)
    assert response.status_code == 404

    response = api_client.delete(api_routes.recipes_slug("test"), headers=unique_user.token)
    assert response.status_code == 404

    response = api_client.patch(api_routes.recipes_slug("test"), json={"test": "stest"}, headers=unique_user.token)
    assert response.status_code == 404


def test_create_recipe_same_name(api_client: TestClient, unique_user: TestUser):
    slug = random_string(10)

    response = api_client.post(api_routes.recipes, json={"name": slug}, headers=unique_user.token)
    assert response.status_code == 201
    assert json.loads(response.text) == slug

    response = api_client.post(api_routes.recipes, json={"name": slug}, headers=unique_user.token)
    assert response.status_code == 201
    assert json.loads(response.text) == f"{slug}-1"


def test_create_recipe_too_many_time(api_client: TestClient, unique_user: TestUser):
    slug = random_string(10)

    for _ in range(10):
        response = api_client.post(api_routes.recipes, json={"name": slug}, headers=unique_user.token)
        assert response.status_code == 201

    response = api_client.post(api_routes.recipes, json={"name": slug}, headers=unique_user.token)
    assert response.status_code == 400


def test_delete_recipe_same_name(api_client: TestClient, unique_user: utils.TestUser, g2_user: utils.TestUser):
    slug = random_string(10)

    # Create recipe for both users
    for user in (unique_user, g2_user):
        response = api_client.post(api_routes.recipes, json={"name": slug}, headers=user.token)
        assert response.status_code == 201
        assert json.loads(response.text) == slug

    # Delete recipe for user 1
    response = api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    assert response.status_code == 200

    # Ensure recipe for user 2 still exists
    response = api_client.get(api_routes.recipes_slug(slug), headers=g2_user.token)
    assert response.status_code == 200

    # Make sure recipe for user 1 doesn't exist
    response = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
    response = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
    assert response.status_code == 404


def test_get_recipe_by_slug_or_id(api_client: TestClient, unique_user: utils.TestUser):
    slugs = [random_string(10) for _ in range(3)]

    # Create recipes
    for slug in slugs:
        response = api_client.post(api_routes.recipes, json={"name": slug}, headers=unique_user.token)
        assert response.status_code == 201
        assert json.loads(response.text) == slug

    # Get recipes by slug
    recipe_ids = []
    for slug in slugs:
        response = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
        assert response.status_code == 200
        recipe_data = response.json()
        assert recipe_data["slug"] == slug
        recipe_ids.append(recipe_data["id"])

    # Get recipes by id
    for recipe_id, slug in zip(recipe_ids, slugs, strict=True):
        response = api_client.get(api_routes.recipes_slug(recipe_id), headers=unique_user.token)
        assert response.status_code == 200
        recipe_data = response.json()
        assert recipe_data["slug"] == slug
        assert recipe_data["id"] == recipe_id


@pytest.mark.parametrize("organizer_type", ["tags", "categories", "tools"])
def test_get_recipes_organizer_filter(api_client: TestClient, unique_user: utils.TestUser, organizer_type: str):
    database = unique_user.repos

    # create recipes with different organizers
    tags = database.tags.create_many([TagSave(name=random_string(), group_id=unique_user.group_id) for _ in range(3)])
    categories = database.categories.create_many(
        [CategorySave(name=random_string(), group_id=unique_user.group_id) for _ in range(3)]
    )
    tools = database.tools.create_many(
        [RecipeToolSave(name=random_string(), group_id=unique_user.group_id) for _ in range(3)]
    )

    new_recipes_data: list[dict] = []
    for i in range(40):
        name = random_string()
        new_recipes_data.append(
            Recipe(
                id=uuid4(),
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=name,
                slug=name,
                tags=[random.choice(tags)] if i % 2 else [],
                recipe_category=[random.choice(categories)] if i % 2 else [],
                tools=[random.choice(tools)] if i % 2 else [],
            )
        )

    recipes = database.recipes.create_many(new_recipes_data)  # type: ignore

    # get recipes by organizer
    if organizer_type == "tags":
        organizer = random.choice(tags)
        expected_recipe_ids = {
            str(recipe.id) for recipe in recipes if organizer.id in [tag.id for tag in recipe.tags or []]
        }
    elif organizer_type == "categories":
        organizer = random.choice(categories)
        expected_recipe_ids = {
            str(recipe.id)
            for recipe in recipes
            if organizer.id in [category.id for category in recipe.recipe_category or []]
        }
    elif organizer_type == "tools":
        organizer = random.choice(tools)
        expected_recipe_ids = {
            str(recipe.id) for recipe in recipes if organizer.id in [tool.id for tool in recipe.tools or []]
        }
    else:
        raise ValueError(f"Unknown organizer type: {organizer_type}")

    query_params = {organizer_type: str(organizer.id)}
    response = api_client.get(api_routes.recipes, params=query_params, headers=unique_user.token)
    assert response.status_code == 200

    response_json = response.json()
    assert len(response_json["items"]) == len(expected_recipe_ids)
    fetched_recipes_ids = [recipe["id"] for recipe in response_json["items"]]
    assert set(fetched_recipes_ids) == expected_recipe_ids


def test_get_random_order(api_client: TestClient, unique_user: utils.TestUser):
    # Create more recipes for stable random ordering
    slugs = [random_string(10) for _ in range(7)]
    for slug in slugs:
        response = api_client.post(api_routes.recipes, json={"name": slug}, headers=unique_user.token)
        assert response.status_code == 201
        assert json.loads(response.text) == slug

    goodparams: dict[str, int | str] = {"page": 1, "perPage": -1, "orderBy": "random", "paginationSeed": "abcdefg"}
    response = api_client.get(api_routes.recipes, params=goodparams, headers=unique_user.token)
    assert response.status_code == 200

    seed1_params: dict[str, int | str] = {"page": 1, "perPage": -1, "orderBy": "random", "paginationSeed": "abcdefg"}
    seed2_params: dict[str, int | str] = {"page": 1, "perPage": -1, "orderBy": "random", "paginationSeed": "gfedcba"}
    data1 = api_client.get(api_routes.recipes, params=seed1_params, headers=unique_user.token).json()
    data2 = api_client.get(api_routes.recipes, params=seed2_params, headers=unique_user.token).json()
    data1_new = api_client.get(api_routes.recipes, params=seed1_params, headers=unique_user.token).json()
    assert data1["items"][0]["slug"] != data2["items"][0]["slug"]  # new seed -> new order
    assert data1["items"][0]["slug"] == data1_new["items"][0]["slug"]  # same seed -> same order

    badparams: dict[str, int | str] = {"page": 1, "perPage": -1, "orderBy": "random"}
    response = api_client.get(api_routes.recipes, params=badparams, headers=unique_user.token)
    assert response.status_code == 422


def test_get_cookbook_recipes(api_client: TestClient, unique_user: utils.TestUser):
    tag = unique_user.repos.tags.create(TagSave(name=random_string(), group_id=unique_user.group_id))
    cookbook_recipes = unique_user.repos.recipes.create_many(
        [
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                tags=[tag],
            )
            for _ in range(3)
        ]
    )
    other_recipes = unique_user.repos.recipes.create_many(
        [
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
            )
            for _ in range(3)
        ]
    )

    cookbook = unique_user.repos.cookbooks.create(
        SaveCookBook(
            name=random_string(),
            group_id=unique_user.group_id,
            household_id=unique_user.household_id,
            query_filter_string=f'tags.id IN ["{tag.id}"]',
        )
    )

    response = api_client.get(api_routes.recipes, params={"cookbook": cookbook.slug}, headers=unique_user.token)
    assert response.status_code == 200
    recipes = [Recipe.model_validate(data) for data in response.json()["items"]]

    fetched_recipe_ids = {recipe.id for recipe in recipes}
    for recipe in cookbook_recipes:
        assert recipe.id in fetched_recipe_ids
    for recipe in other_recipes:
        assert recipe.id not in fetched_recipe_ids
