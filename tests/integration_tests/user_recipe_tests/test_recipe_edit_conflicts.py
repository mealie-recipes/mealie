from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def create_recipe(client: TestClient, user: TestUser) -> dict:
    response = client.post(api_routes.recipes, json={"name": random_string()}, headers=user.token)
    assert response.status_code == 201
    return client.get(api_routes.recipes_slug(response.json()), headers=user.token).json()


@pytest.mark.parametrize("method", ["put", "patch"])
def test_stale_recipe_edit(api_client: TestClient, unique_user: TestUser, method: str):
    original = create_recipe(api_client, unique_user)
    url = api_routes.recipes_slug(original["slug"])
    first = deepcopy(original)
    first["description"] = "first editor"
    saved = getattr(api_client, method)(url, json=first, headers=unique_user.token)
    assert saved.status_code == 200
    assert saved.json()["updatedAt"] != original["updatedAt"]
    stale = deepcopy(original)
    stale["description"] = "stale editor"
    rejected = getattr(api_client, method)(url, json=stale, headers=unique_user.token)
    assert rejected.status_code == 409
    current = api_client.get(url, headers=unique_user.token).json()
    assert current["description"] == "first editor"
    assert current["updatedAt"] == saved.json()["updatedAt"]
    current["description"] = "refreshed editor"
    assert getattr(api_client, method)(url, json=current, headers=unique_user.token).status_code == 200


@pytest.mark.parametrize("method", ["put", "patch"])
def test_legacy_updates_without_timestamp(api_client: TestClient, unique_user: TestUser, method: str):
    original = create_recipe(api_client, unique_user)
    payload = deepcopy(original)
    payload.pop("updatedAt")
    payload["description"] = "legacy client"
    response = getattr(api_client, method)(
        api_routes.recipes_slug(original["slug"]), json=payload, headers=unique_user.token
    )
    assert response.status_code == 200
    assert response.json()["updatedAt"] != original["updatedAt"]


@pytest.mark.parametrize("method", ["put", "patch"])
def test_bulk_conflict_rolls_back(api_client: TestClient, unique_user: TestUser, method: str):
    first = create_recipe(api_client, unique_user)
    second = create_recipe(api_client, unique_user)
    changed = deepcopy(second)
    changed["description"] = "already updated"
    assert (
        api_client.put(api_routes.recipes_slug(second["slug"]), json=changed, headers=unique_user.token).status_code
        == 200
    )
    first_change = deepcopy(first)
    first_change["description"] = "must roll back"
    response = getattr(api_client, method)(api_routes.recipes, json=[first_change, second], headers=unique_user.token)
    assert response.status_code == 409
    after = api_client.get(api_routes.recipes_slug(first["slug"]), headers=unique_user.token).json()
    assert after["description"] == first["description"]
    assert after["updatedAt"] == first["updatedAt"]


def test_image_version_and_stale_delete(api_client: TestClient, unique_user: TestUser):
    original = create_recipe(api_client, unique_user)
    url = api_routes.recipes_slug(original["slug"])
    headers = {**unique_user.token, "X-Recipe-Updated-At": original["updatedAt"]}
    deleted = api_client.delete(url + "/image", headers=headers)
    assert deleted.status_code == 200
    timestamp = deleted.headers["X-Recipe-Updated-At"]
    current = api_client.get(url, headers=unique_user.token).json()
    from datetime import datetime

    assert datetime.fromisoformat(timestamp) == datetime.fromisoformat(current["updatedAt"])
    assert api_client.delete(url + "/image", headers=headers).status_code == 409
    current["description"] = "save after own image edit"
    current["updatedAt"] = timestamp
    assert api_client.put(url, json=current, headers=unique_user.token).status_code == 200


def test_relationship_only_edit_advances_time(api_client: TestClient, unique_user: TestUser):
    recipe = create_recipe(api_client, unique_user)
    response = api_client.patch(
        api_routes.recipes_slug(recipe["slug"]),
        headers=unique_user.token,
        json={"updatedAt": recipe["updatedAt"], "notes": [{"title": "Note", "text": "New note"}]},
    )
    assert response.status_code == 200
    assert response.json()["updatedAt"] != recipe["updatedAt"]


def test_simultaneous_edit_only_one_wins(api_client: TestClient, unique_user: TestUser, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from mealie.app import app
    from mealie.repos.repository_recipes import RepositoryRecipes

    original = create_recipe(api_client, unique_user)
    barrier = Barrier(2)
    reserve = RepositoryRecipes.reserve_update

    def synchronized_reserve(self, match_value, expected=None):
        barrier.wait(timeout=10)
        return reserve(self, match_value, expected)

    monkeypatch.setattr(RepositoryRecipes, "reserve_update", synchronized_reserve)

    def save(description):
        payload = {**original, "description": description}
        with TestClient(app) as client:
            return client.put(api_routes.recipes_slug(original["slug"]), headers=unique_user.token, json=payload)

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(save, ["editor A", "editor B"]))
    assert sorted(response.status_code for response in responses) == [200, 409]
    winner = next(response.json() for response in responses if response.status_code == 200)
    actual = api_client.get(api_routes.recipes_slug(original["slug"]), headers=unique_user.token).json()
    assert actual["description"] == winner["description"]
    assert actual["updatedAt"] == winner["updatedAt"]


def test_image_upload_returns_exact_version(api_client: TestClient, unique_user: TestUser, test_image_jpg):
    recipe = create_recipe(api_client, unique_user)
    url = api_routes.recipes_slug(recipe["slug"])
    headers = {**unique_user.token, "X-Recipe-Updated-At": recipe["updatedAt"]}
    response = api_client.put(
        url + "/image",
        headers=headers,
        data={"extension": "jpg"},
        files={"image": ("test.jpg", test_image_jpg.read_bytes(), "image/jpeg")},
    )
    assert response.status_code == 200
    current = api_client.get(url, headers=unique_user.token).json()
    from datetime import datetime

    assert datetime.fromisoformat(response.headers["X-Recipe-Updated-At"]) == datetime.fromisoformat(
        current["updatedAt"]
    )
    assert api_client.delete(url + "/image", headers=headers).status_code == 409
    assert api_client.get(url, headers=unique_user.token).json()["image"] == current["image"]
