import pytest
from fastapi.testclient import TestClient
from pydantic import UUID4

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_timeline_events import RecipeTimelineEventOut
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/recipes"

    @staticmethod
    def event_base(slug: str) -> str:
        return f"{Routes.base}/{slug}/timeline/events"

    @staticmethod
    def event_item(slug: str, item_id: str | UUID4) -> str:
        return f"{Routes.event_base(slug)}/{item_id}"


@pytest.fixture(scope="function")
def recipes(api_client: TestClient, unique_user: TestUser):
    recipes = []
    for _ in range(3):
        data = {"name": random_string(10)}
        response = api_client.post(Routes.base, json=data, headers=unique_user.token)

        assert response.status_code == 201
        slug = response.json()

        response = api_client.get(f"{Routes.base}/{slug}", headers=unique_user.token)
        assert response.status_code == 200

        recipe = Recipe.parse_obj(response.json())
        recipes.append(recipe)

    yield recipes
    response = api_client.delete(f"{Routes.base}/{slug}", headers=unique_user.token)


def test_create_timeline_event(api_client: TestClient, unique_user: TestUser, recipes: list[Recipe]):
    recipe = recipes[0]
    new_event = {
        "user_id": unique_user.user_id,
        "subject": random_string(),
        "event_type": "info",
        "message": random_string(),
    }

    event_response = api_client.post(Routes.event_base(recipe.slug), json=new_event, headers=unique_user.token)
    assert event_response.status_code == 201

    event = RecipeTimelineEventOut.parse_obj(event_response.json())
    assert event.recipe_id == recipe.id
    assert str(event.user_id) == str(unique_user.user_id)


def test_get_timeline_event(api_client: TestClient, unique_user: TestUser, recipes: list[Recipe]):
    # create an event
    recipe = recipes[0]
    new_event_data = {
        "user_id": unique_user.user_id,
        "subject": random_string(),
        "event_type": "info",
        "message": random_string(),
    }

    event_response = api_client.post(Routes.event_base(recipe.slug), json=new_event_data, headers=unique_user.token)
    new_event = RecipeTimelineEventOut.parse_obj(event_response.json())

    # fetch the new event
    event_response = api_client.get(Routes.event_item(recipe.slug, new_event.id), headers=unique_user.token)
    assert event_response.status_code == 200

    event = RecipeTimelineEventOut.parse_obj(event_response.json())
    assert event == new_event


def test_update_timeline_event(api_client: TestClient, unique_user: TestUser, recipes: list[Recipe]):
    old_subject = random_string()
    new_subject = random_string()

    # create an event
    recipe = recipes[0]
    new_event_data = {
        "user_id": unique_user.user_id,
        "subject": old_subject,
        "event_type": "info",
    }

    event_response = api_client.post(Routes.event_base(recipe.slug), json=new_event_data, headers=unique_user.token)
    new_event = RecipeTimelineEventOut.parse_obj(event_response.json())
    assert new_event.subject == old_subject

    # update the event
    updated_event_data = {"subject": new_subject}

    event_response = api_client.put(
        Routes.event_item(recipe.slug, new_event.id), json=updated_event_data, headers=unique_user.token
    )
    assert event_response.status_code == 200

    updated_event = RecipeTimelineEventOut.parse_obj(event_response.json())
    assert new_event.id == updated_event.id
    assert updated_event.subject == new_subject


def test_delete_timeline_event(api_client: TestClient, unique_user: TestUser, recipes: list[Recipe]):
    # create an event
    recipe = recipes[0]
    new_event_data = {
        "user_id": unique_user.user_id,
        "subject": random_string(),
        "event_type": "info",
        "message": random_string(),
    }

    event_response = api_client.post(Routes.event_base(recipe.slug), json=new_event_data, headers=unique_user.token)
    new_event = RecipeTimelineEventOut.parse_obj(event_response.json())

    # delete the event
    event_response = api_client.delete(Routes.event_item(recipe.slug, new_event.id), headers=unique_user.token)
    assert event_response.status_code == 200

    deleted_event = RecipeTimelineEventOut.parse_obj(event_response.json())
    assert deleted_event.id == new_event.id

    # try to get the event
    event_response = api_client.get(Routes.event_item(recipe.slug, deleted_event.id), headers=unique_user.token)
    assert event_response.status_code == 404


def test_invalid_recipe_slug(api_client: TestClient, unique_user: TestUser):
    new_event_data = {
        "user_id": unique_user.user_id,
        "subject": random_string(),
        "event_type": "info",
        "message": random_string(),
    }

    event_response = api_client.post(Routes.event_base(random_string()), json=new_event_data, headers=unique_user.token)
    assert event_response.status_code == 404


def test_recipe_slug_mismatch(api_client: TestClient, unique_user: TestUser, recipes: list[Recipe]):
    # get new recipes
    recipe = recipes[0]
    invalid_recipe = recipes[1]

    # create a new event
    new_event_data = {
        "user_id": unique_user.user_id,
        "subject": random_string(),
        "event_type": "info",
        "message": random_string(),
    }

    event_response = api_client.post(Routes.event_base(recipe.slug), json=new_event_data, headers=unique_user.token)
    event = RecipeTimelineEventOut.parse_obj(event_response.json())

    # try to perform operations on the event using the wrong recipe
    event_response = api_client.get(
        Routes.event_item(invalid_recipe.slug, event.id), json=new_event_data, headers=unique_user.token
    )
    assert event_response.status_code == 404

    event_response = api_client.put(
        Routes.event_item(invalid_recipe.slug, event.id), json=new_event_data, headers=unique_user.token
    )
    assert event_response.status_code == 404

    event_response = api_client.delete(
        Routes.event_item(invalid_recipe.slug, event.id), json=new_event_data, headers=unique_user.token
    )
    assert event_response.status_code == 404

    # make sure the event still exists and is unmodified
    event_response = api_client.get(
        Routes.event_item(recipe.slug, event.id), json=new_event_data, headers=unique_user.token
    )
    assert event_response.status_code == 200

    existing_event = RecipeTimelineEventOut.parse_obj(event_response.json())
    assert existing_event == event
