import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from recipe_scrapers._abstract import AbstractScraper
from recipe_scrapers._schemaorg import SchemaOrg
from slugify import slugify

from mealie.schema.recipe.recipe import RecipeCategory
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.scraper.recipe_scraper import DEFAULT_SCRAPER_STRATEGIES
from tests import data, utils
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser
from tests.utils.recipe_data import RecipeSiteTestCase, get_recipe_test_cases

recipe_test_data = get_recipe_test_cases()


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

    return init_override


def open_graph_override(html: str):
    async def get_html(self, url: str) -> str:
        return html

    return get_html


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_create_by_url(
    api_client: TestClient,
    recipe_data: RecipeSiteTestCase,
    unique_user: TestUser,
    monkeypatch: MonkeyPatch,
):
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
    # Skip image downloader
    monkeypatch.setattr(
        RecipeDataService,
        "scrape_image",
        lambda *_: "TEST_IMAGE",
    )

    api_client.delete(api_routes.recipes_slug(recipe_data.expected_slug), headers=unique_user.token)

    response = api_client.post(
        api_routes.recipes_create_url, json={"url": recipe_data.url, "include_tags": False}, headers=unique_user.token
    )

    assert response.status_code == 201
    assert json.loads(response.text) == recipe_data.expected_slug

    recipe = api_client.get(api_routes.recipes_slug(recipe_data.expected_slug), headers=unique_user.token)

    assert recipe.status_code == 200

    recipe_dict: dict = json.loads(recipe.text)

    assert recipe_dict["slug"] == recipe_data.expected_slug
    assert len(recipe_dict["recipeInstructions"]) == recipe_data.num_steps
    assert len(recipe_dict["recipeIngredient"]) == recipe_data.num_ingredients


def test_create_by_url_with_tags(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: MonkeyPatch,
):
    html_file = data.html_nutty_umami_noodles_with_scallion_brown_butter_and_snow_peas_recipe

    # Override init function for AbstractScraper to use the test html instead of calling the url
    monkeypatch.setattr(
        AbstractScraper,
        "__init__",
        get_init(html_file),
    )
    # Override the get_html method of all scraper strategies to return the test html
    for scraper_cls in DEFAULT_SCRAPER_STRATEGIES:
        monkeypatch.setattr(
            scraper_cls,
            "get_html",
            open_graph_override(html_file.read_text()),
        )
    # Skip image downloader
    monkeypatch.setattr(
        RecipeDataService,
        "scrape_image",
        lambda *_: "TEST_IMAGE",
    )

    response = api_client.post(
        api_routes.recipes_create_url,
        json={"url": "https://google.com", "include_tags": True},  # URL Doesn't matter
        headers=unique_user.token,
    )
    assert response.status_code == 201
    slug = "nutty-umami-noodles-with-scallion-brown-butter-and-snow-peas"

    # Get the recipe
    response = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
    assert response.status_code == 200

    # Verifiy the tags are present and title cased
    expected_tags = {
        "Sauté",
        "Pea",
        "Noodle",
        "Udon Noodle",
        "Ramen Noodle",
        "Dinner",
        "Main",
        "Vegetarian",
        "Easy",
        "Quick",
        "Weeknight Meals",
        "Web",
    }

    recipe = json.loads(response.text)

    assert len(recipe["tags"]) == len(expected_tags)

    for tag in recipe["tags"]:
        assert tag["name"] in expected_tags


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_read_update(
    api_client: TestClient,
    recipe_data: RecipeSiteTestCase,
    unique_user: TestUser,
    recipe_categories: list[RecipeCategory],
):
    recipe_url = api_routes.recipes_slug(recipe_data.expected_slug)
    response = api_client.get(recipe_url, headers=unique_user.token)
    assert response.status_code == 200

    recipe = json.loads(response.text)

    test_notes = [
        {"title": "My Test Title1", "text": "My Test Text1"},
        {"title": "My Test Title2", "text": "My Test Text2"},
    ]

    recipe["notes"] = test_notes

    recipe["recipeCategory"] = [x.dict() for x in recipe_categories]

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


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_duplicate(api_client: TestClient, recipe_data: RecipeSiteTestCase, unique_user: TestUser):
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
    assert list(map(lambda i: i["note"], duplicate_recipe["recipeIngredient"])) == list(
        map(lambda i: i["note"], initial_recipe["recipeIngredient"])
    )

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
@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_update_with_empty_relationship(
    api_client: TestClient,
    recipe_data: RecipeSiteTestCase,
    unique_user: TestUser,
):
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


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_rename(api_client: TestClient, recipe_data: RecipeSiteTestCase, unique_user: TestUser):
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


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_delete(api_client: TestClient, recipe_data: RecipeSiteTestCase, unique_user: TestUser):
    response = api_client.delete(api_routes.recipes_slug(recipe_data.expected_slug), headers=unique_user.token)
    assert response.status_code == 200


def test_recipe_crud_404(api_client: TestClient, unique_user: TestUser):
    response = api_client.put(api_routes.recipes_slug("test"), json={"test": "stest"}, headers=unique_user.token)
    assert response.status_code == 404

    response = api_client.get(api_routes.recipes_slug("test"), headers=unique_user.token)
    assert response.status_code == 404

    response = api_client.delete(api_routes.recipes_slug("test"), headers=unique_user.token)
    assert response.status_code == 404

    response = api_client.patch(api_routes.recipes_create_url, json={"test": "stest"}, headers=unique_user.token)
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
