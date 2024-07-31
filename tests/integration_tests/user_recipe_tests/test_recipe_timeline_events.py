from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_timeline_events import (
    RecipeTimelineEventOut,
    RecipeTimelineEventPagination,
    TimelineEventImage,
)
from mealie.schema.recipe.request_helpers import UpdateImageResponse
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


@pytest.fixture(scope="function")
def recipes(api_client: TestClient, unique_user: TestUser):
    recipes = []
    for _ in range(3):
        data = {"name": random_string(10)}
        response = api_client.post(api_routes.recipes, json=data, headers=unique_user.token)

        assert response.status_code == 201
        slug = response.json()

        response = api_client.get(f"{api_routes.recipes}/{slug}", headers=unique_user.token)
        assert response.status_code == 200

        recipe = Recipe.model_validate(response.json())
        recipes.append(recipe)

    yield recipes
    response = api_client.delete(f"{api_routes.recipes}/{slug}", headers=unique_user.token)


def test_create_timeline_event(api_client: TestClient, unique_user: TestUser, recipes: list[Recipe]):
    recipe = recipes[0]
    new_event = {
        "recipe_id": str(recipe.id),
        "user_id": str(unique_user.user_id),
        "subject": random_string(),
        "event_type": "info",
        "message": random_string(),
    }

    event_response = api_client.post(
        api_routes.recipes_timeline_events,
        json=new_event,
        headers=unique_user.token,
    )
    assert event_response.status_code == 201

    event = RecipeTimelineEventOut.model_validate(event_response.json())
    assert event.recipe_id == recipe.id
    assert str(event.user_id) == str(unique_user.user_id)


def test_get_all_timeline_events(api_client: TestClient, unique_user: TestUser, recipes: list[Recipe]):
    # create some events
    recipe = recipes[0]
    events_data = [
        {
            "recipe_id": str(recipe.id),
            "user_id": str(unique_user.user_id),
            "subject": random_string(),
            "event_type": "info",
            "message": random_string(),
        }
        for _ in range(10)
    ]

    events: list[RecipeTimelineEventOut] = []
    for event_data in events_data:
        params: dict = {"queryFilter": f"recipe_id={event_data['recipe_id']}"}
        event_response = api_client.post(
            api_routes.recipes_timeline_events, params=params, json=event_data, headers=unique_user.token
        )
        events.append(RecipeTimelineEventOut.model_validate(event_response.json()))

    # check that we see them all
    params = {"page": 1, "perPage": -1}

    events_response = api_client.get(api_routes.recipes_timeline_events, params=params, headers=unique_user.token)
    events_pagination = RecipeTimelineEventPagination.model_validate(events_response.json())

    event_ids = [event.id for event in events]
    paginated_event_ids = [event.id for event in events_pagination.items]

    assert len(event_ids) <= len(paginated_event_ids)
    for event_id in event_ids:
        assert event_id in paginated_event_ids


def test_get_timeline_event(api_client: TestClient, unique_user: TestUser, recipes: list[Recipe]):
    # create an event
    recipe = recipes[0]
    new_event_data = {
        "recipe_id": str(recipe.id),
        "user_id": str(unique_user.user_id),
        "subject": random_string(),
        "event_type": "info",
        "message": random_string(),
    }

    event_response = api_client.post(
        api_routes.recipes_timeline_events,
        json=new_event_data,
        headers=unique_user.token,
    )
    new_event = RecipeTimelineEventOut.model_validate(event_response.json())

    # fetch the new event
    event_response = api_client.get(api_routes.recipes_timeline_events_item_id(new_event.id), headers=unique_user.token)
    assert event_response.status_code == 200

    event = RecipeTimelineEventOut.model_validate(event_response.json())
    assert event == new_event


def test_update_timeline_event(api_client: TestClient, unique_user: TestUser, recipes: list[Recipe]):
    old_subject = random_string()
    new_subject = random_string()

    # create an event
    recipe = recipes[0]
    new_event_data = {
        "recipe_id": str(recipe.id),
        "user_id": str(unique_user.user_id),
        "subject": old_subject,
        "event_type": "info",
    }

    event_response = api_client.post(api_routes.recipes_timeline_events, json=new_event_data, headers=unique_user.token)
    new_event = RecipeTimelineEventOut.model_validate(event_response.json())
    assert new_event.subject == old_subject

    # update the event
    updated_event_data = {"subject": new_subject}

    event_response = api_client.put(
        api_routes.recipes_timeline_events_item_id(new_event.id),
        json=updated_event_data,
        headers=unique_user.token,
    )
    assert event_response.status_code == 200

    updated_event = RecipeTimelineEventOut.model_validate(event_response.json())
    assert updated_event.id == new_event.id
    assert updated_event.subject == new_subject
    assert updated_event.timestamp == new_event.timestamp


def test_delete_timeline_event(api_client: TestClient, unique_user: TestUser, recipes: list[Recipe]):
    # create an event
    recipe = recipes[0]
    new_event_data = {
        "recipe_id": str(recipe.id),
        "user_id": str(unique_user.user_id),
        "subject": random_string(),
        "event_type": "info",
        "message": random_string(),
    }

    event_response = api_client.post(api_routes.recipes_timeline_events, json=new_event_data, headers=unique_user.token)
    new_event = RecipeTimelineEventOut.model_validate(event_response.json())

    # delete the event
    event_response = api_client.delete(
        api_routes.recipes_timeline_events_item_id(new_event.id), headers=unique_user.token
    )
    assert event_response.status_code == 200

    deleted_event = RecipeTimelineEventOut.model_validate(event_response.json())
    assert deleted_event.id == new_event.id

    # try to get the event
    event_response = api_client.get(
        api_routes.recipes_timeline_events_item_id(deleted_event.id), headers=unique_user.token
    )
    assert event_response.status_code == 404


def test_timeline_event_message_alias(api_client: TestClient, unique_user: TestUser, recipes: list[Recipe]):
    # create an event using aliases
    recipe = recipes[0]
    new_event_data = {
        "recipeId": str(recipe.id),
        "userId": str(unique_user.user_id),
        "subject": random_string(),
        "eventType": "info",
        "eventMessage": random_string(),  # eventMessage is the correct alias for the message
    }

    event_response = api_client.post(
        api_routes.recipes_timeline_events,
        json=new_event_data,
        headers=unique_user.token,
    )
    new_event = RecipeTimelineEventOut.model_validate(event_response.json())
    assert str(new_event.user_id) == new_event_data["userId"]
    assert str(new_event.event_type) == new_event_data["eventType"]
    assert new_event.message == new_event_data["eventMessage"]

    # fetch the new event
    event_response = api_client.get(api_routes.recipes_timeline_events_item_id(new_event.id), headers=unique_user.token)
    assert event_response.status_code == 200

    event = RecipeTimelineEventOut.model_validate(event_response.json())
    assert event == new_event

    # update the event message
    new_subject = random_string()
    new_message = random_string()
    updated_event_data = {"subject": new_subject, "eventMessage": new_message}

    event_response = api_client.put(
        api_routes.recipes_timeline_events_item_id(new_event.id),
        json=updated_event_data,
        headers=unique_user.token,
    )
    assert event_response.status_code == 200

    updated_event = RecipeTimelineEventOut.model_validate(event_response.json())
    assert updated_event.subject == new_subject
    assert updated_event.message == new_message


def test_timeline_event_update_image(
    api_client: TestClient, unique_user: TestUser, recipes: list[Recipe], test_image_jpg: str
):
    # create an event
    recipe = recipes[0]
    new_event_data = {
        "recipe_id": str(recipe.id),
        "user_id": str(unique_user.user_id),
        "subject": random_string(),
        "message": random_string(),
        "event_type": "info",
    }

    event_response = api_client.post(api_routes.recipes_timeline_events, json=new_event_data, headers=unique_user.token)
    new_event = RecipeTimelineEventOut.model_validate(event_response.json())
    assert new_event.image == TimelineEventImage.does_not_have_image.value

    with open(test_image_jpg, "rb") as f:
        r = api_client.put(
            api_routes.recipes_timeline_events_item_id_image(new_event.id),
            files={"image": ("test_image_jpg.jpg", f, "image/jpeg")},
            data={"extension": "jpg"},
            headers=unique_user.token,
        )
    r.raise_for_status()

    update_image_response = UpdateImageResponse.model_validate(r.json())
    assert update_image_response.image == TimelineEventImage.has_image.value

    event_response = api_client.get(
        api_routes.recipes_timeline_events_item_id(new_event.id),
        headers=unique_user.token,
    )
    assert event_response.status_code == 200

    updated_event = RecipeTimelineEventOut.model_validate(event_response.json())
    assert updated_event.subject == new_event.subject
    assert updated_event.message == new_event.message
    assert updated_event.timestamp == new_event.timestamp
    assert updated_event.image == TimelineEventImage.has_image.value


def test_create_recipe_with_timeline_event(api_client: TestClient, unique_user: TestUser, recipes: list[Recipe]):
    # make sure when the recipes fixture was created that all recipes have at least one event
    for recipe in recipes:
        params = {"queryFilter": f"recipe_id={recipe.id}"}
        events_response = api_client.get(api_routes.recipes_timeline_events, params=params, headers=unique_user.token)
        events_pagination = RecipeTimelineEventPagination.model_validate(events_response.json())
        assert events_pagination.items


def test_invalid_recipe_id(api_client: TestClient, unique_user: TestUser):
    new_event_data = {
        "recipe_id": str(uuid4()),
        "user_id": str(unique_user.user_id),
        "subject": random_string(),
        "event_type": "info",
        "message": random_string(),
    }

    event_response = api_client.post(api_routes.recipes_timeline_events, json=new_event_data, headers=unique_user.token)
    assert event_response.status_code == 404
