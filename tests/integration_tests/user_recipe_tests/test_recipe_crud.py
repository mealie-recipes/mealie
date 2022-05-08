import json
from pathlib import Path
from typing import Optional, Union

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from recipe_scrapers._abstract import AbstractScraper
from recipe_scrapers._schemaorg import SchemaOrg
from slugify import slugify

from mealie.schema.recipe.recipe import RecipeCategory
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.scraper.scraper_strategies import RecipeScraperOpenGraph
from tests import data, utils
from tests.utils import routes
from tests.utils.app_routes import AppRoutes
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
        proxies: Optional[str] = None,
        timeout: Optional[Union[float, tuple, None]] = None,
        wild_mode: Optional[bool] = False,
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
    def get_html(self) -> str:
        return html

    return get_html


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_create_by_url(
    api_client: TestClient,
    api_routes: AppRoutes,
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
    monkeypatch.setattr(
        RecipeScraperOpenGraph,
        "get_html",
        open_graph_override(recipe_data.html_file.read_text()),
    )
    # Skip image downloader
    monkeypatch.setattr(
        RecipeDataService,
        "scrape_image",
        lambda *_: "TEST_IMAGE",
    )

    api_client.delete(api_routes.recipes_recipe_slug(recipe_data.expected_slug), headers=unique_user.token)

    response = api_client.post(
        api_routes.recipes_create_url, json={"url": recipe_data.url, "include_tags": False}, headers=unique_user.token
    )

    assert response.status_code == 201
    assert json.loads(response.text) == recipe_data.expected_slug


def test_create_by_url_with_tags(
    api_client: TestClient,
    api_routes: AppRoutes,
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
    # Override the get_html method of the RecipeScraperOpenGraph to return the test html
    monkeypatch.setattr(
        RecipeScraperOpenGraph,
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
    response = api_client.get(api_routes.recipes_recipe_slug(slug), headers=unique_user.token)
    assert response.status_code == 200

    # Verifiy the tags are present
    expected_tags = {
        "sauté",
        "pea",
        "noodle",
        "udon noodle",
        "ramen noodle",
        "dinner",
        "main",
        "vegetarian",
        "easy",
        "quick",
        "weeknight meals",
        "web",
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
    recipe_url = routes.recipes.Recipe.item(recipe_data.expected_slug)
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
    for cats in zip(recipe["recipeCategory"], recipe_categories):
        assert cats[0]["name"] in test_name


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_rename(api_client: TestClient, recipe_data: RecipeSiteTestCase, unique_user: TestUser):
    recipe_url = routes.recipes.Recipe.item(recipe_data.expected_slug)
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
    response = api_client.delete(routes.recipes.Recipe.item(recipe_data.expected_slug), headers=unique_user.token)
    assert response.status_code == 200


def test_recipe_crud_404(api_client: TestClient, api_routes: AppRoutes, unique_user: TestUser):
    response = api_client.put(routes.recipes.Recipe.item("test"), json={"test": "stest"}, headers=unique_user.token)
    assert response.status_code == 404

    response = api_client.get(routes.recipes.Recipe.item("test"), headers=unique_user.token)
    assert response.status_code == 404

    response = api_client.delete(routes.recipes.Recipe.item("test"), headers=unique_user.token)
    assert response.status_code == 404

    response = api_client.patch(api_routes.recipes_create_url, json={"test": "stest"}, headers=unique_user.token)
    assert response.status_code == 404


def test_create_recipe_same_name(api_client: TestClient, unique_user: TestUser):
    slug = random_string(10)

    response = api_client.post(routes.recipes.Recipe.base, json={"name": slug}, headers=unique_user.token)
    assert response.status_code == 201
    assert json.loads(response.text) == slug

    response = api_client.post(routes.recipes.Recipe.base, json={"name": slug}, headers=unique_user.token)
    assert response.status_code == 201
    assert json.loads(response.text) == f"{slug}-1"


def test_create_recipe_too_many_time(api_client: TestClient, unique_user: TestUser):
    slug = random_string(10)

    for _ in range(10):
        response = api_client.post(routes.recipes.Recipe.base, json={"name": slug}, headers=unique_user.token)
        assert response.status_code == 201

    response = api_client.post(routes.recipes.Recipe.base, json={"name": slug}, headers=unique_user.token)
    assert response.status_code == 400


def test_delete_recipe_same_name(api_client: TestClient, unique_user: utils.TestUser, g2_user: utils.TestUser):
    slug = random_string(10)

    # Create recipe for both users
    for user in (unique_user, g2_user):
        response = api_client.post(routes.recipes.Recipe.base, json={"name": slug}, headers=user.token)
        assert response.status_code == 201
        assert json.loads(response.text) == slug

    # Delete recipe for user 1
    response = api_client.delete(routes.recipes.Recipe.item(slug), headers=unique_user.token)
    assert response.status_code == 200

    # Ensure recipe for user 2 still exists
    response = api_client.get(routes.recipes.Recipe.item(slug), headers=g2_user.token)
    assert response.status_code == 200

    # Make sure recipe for user 1 doesn't exist
    response = api_client.get(routes.recipes.Recipe.item(slug), headers=unique_user.token)
    response = api_client.get(routes.recipes.Recipe.item(slug), headers=unique_user.token)
    assert response.status_code == 404
