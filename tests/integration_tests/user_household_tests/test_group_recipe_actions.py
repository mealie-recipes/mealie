from uuid import UUID, uuid4

import pytest
import requests
from fastapi.testclient import TestClient

from mealie.schema.household.group_recipe_action import (
    CreateGroupRecipeAction,
    GroupRecipeActionOut,
    GroupRecipeActionType,
    SaveGroupRecipeAction,
)
from mealie.schema.recipe.recipe import Recipe
from tests.utils import api_routes, assert_deserialize
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


@pytest.fixture(autouse=True)
def mock_requests_post(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: None)


def create_action(action_type: GroupRecipeActionType = GroupRecipeActionType.link) -> CreateGroupRecipeAction:
    return CreateGroupRecipeAction(
        action_type=action_type,
        title=random_string(),
        url=random_string(),
    )


def save_action(
    user: TestUser, action_type: GroupRecipeActionType = GroupRecipeActionType.link
) -> SaveGroupRecipeAction:
    action = create_action(action_type)
    return action.cast(SaveGroupRecipeAction, group_id=UUID(user.group_id), household_id=UUID(user.household_id))


def new_recipe(user: TestUser) -> Recipe:
    return Recipe(
        user_id=user.user_id,
        group_id=UUID(user.group_id),
        name=random_string(),
    )


def test_group_recipe_actions_create_one(api_client: TestClient, unique_user: TestUser):
    action_in = create_action()
    response = api_client.post(
        api_routes.households_recipe_actions,
        json=action_in.model_dump(),
        headers=unique_user.token,
    )
    data = assert_deserialize(response, 201)

    action_out = GroupRecipeActionOut(**data)
    assert action_out.id
    assert str(action_out.group_id) == unique_user.group_id
    assert str(action_out.household_id) == unique_user.household_id
    assert action_out.action_type == action_in.action_type
    assert action_out.title == action_in.title
    assert action_out.url == action_in.url


def test_group_recipe_actions_get_all(api_client: TestClient, unique_user: TestUser):
    expected_ids: set[str] = set()
    for _ in range(random_int(3, 5)):
        response = api_client.post(
            api_routes.households_recipe_actions,
            json=create_action().model_dump(),
            headers=unique_user.token,
        )
        data = assert_deserialize(response, 201)
        expected_ids.add(data["id"])

    response = api_client.get(api_routes.households_recipe_actions, headers=unique_user.token)
    data = assert_deserialize(response, 200)
    fetched_ids = {item["id"] for item in data["items"]}
    for expected_id in expected_ids:
        assert expected_id in fetched_ids


@pytest.mark.parametrize("is_own_group", [True, False])
def test_group_recipe_actions_get_one(
    api_client: TestClient, unique_user: TestUser, g2_user: TestUser, is_own_group: bool
):
    action_in = create_action()
    response = api_client.post(
        api_routes.households_recipe_actions,
        json=action_in.model_dump(),
        headers=unique_user.token,
    )
    data = assert_deserialize(response, 201)
    expected_action_out = GroupRecipeActionOut(**data)

    if is_own_group:
        fetch_user = unique_user
    else:
        fetch_user = g2_user

    response = api_client.get(
        api_routes.households_recipe_actions_item_id(expected_action_out.id),
        headers=fetch_user.token,
    )
    if not is_own_group:
        assert response.status_code == 404
        return

    data = assert_deserialize(response, 200)
    action_out = GroupRecipeActionOut(**data)
    assert action_out == expected_action_out


def test_group_recipe_actions_update_one(api_client: TestClient, unique_user: TestUser):
    action_in = create_action()
    response = api_client.post(
        api_routes.households_recipe_actions,
        json=action_in.model_dump(),
        headers=unique_user.token,
    )
    data = assert_deserialize(response, 201)
    action_id = data["id"]

    new_title = random_string()
    data["title"] = new_title
    response = api_client.put(
        api_routes.households_recipe_actions_item_id(action_id),
        json=data,
        headers=unique_user.token,
    )
    data = assert_deserialize(response, 200)
    updated_action = GroupRecipeActionOut(**data)

    assert updated_action.title == new_title


def test_group_recipe_actions_delete_one(api_client: TestClient, unique_user: TestUser):
    action_in = create_action()
    response = api_client.post(
        api_routes.households_recipe_actions,
        json=action_in.model_dump(),
        headers=unique_user.token,
    )
    data = assert_deserialize(response, 201)
    action_id = data["id"]

    response = api_client.delete(api_routes.households_recipe_actions_item_id(action_id), headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.get(api_routes.households_recipe_actions_item_id(action_id), headers=unique_user.token)
    assert response.status_code == 404


@pytest.mark.parametrize("missing_action", [True, False])
@pytest.mark.parametrize("missing_recipe", [True, False])
def test_group_recipe_actions_trigger_post(
    api_client: TestClient, unique_user: TestUser, missing_action: bool, missing_recipe: bool
):
    if missing_action:
        action_id = uuid4()
    else:
        recipe_action = unique_user.repos.group_recipe_actions.create(
            save_action(unique_user, GroupRecipeActionType.post)
        )
        action_id = recipe_action.id

    if missing_recipe:
        recipe_slug = random_string()
    else:
        recipe = unique_user.repos.recipes.create(new_recipe(unique_user))
        recipe_slug = recipe.slug

    response = api_client.post(
        api_routes.households_recipe_actions_item_id_trigger_recipe_slug(action_id, recipe_slug),
        headers=unique_user.token,
    )

    if missing_action or missing_recipe:
        assert response.status_code == 404
    else:
        # we don't test if the request was actually made, just that the endpoint was hit and accepted
        assert response.status_code == 202


def test_group_recipe_actions_trigger_invalid_type(api_client: TestClient, unique_user: TestUser):
    recipe_action = unique_user.repos.group_recipe_actions.create(save_action(unique_user, GroupRecipeActionType.link))
    recipe = unique_user.repos.recipes.create(new_recipe(unique_user))

    response = api_client.post(
        api_routes.households_recipe_actions_item_id_trigger_recipe_slug(recipe_action.id, recipe.id),
        headers=unique_user.token,
    )

    assert response.status_code == 400
