from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

TAGS_ROUTE = "/api/organizers/tags"


def test_update_tag_order(api_client: TestClient, unique_user: TestUser):
    created_tags = []
    for _ in range(3):
        response = api_client.post(TAGS_ROUTE, json={"name": random_string(10)}, headers=unique_user.token)
        assert response.status_code == 201
        created_tags.append(response.json())

    response = api_client.post(api_routes.recipes, json={"name": random_string(10)}, headers=unique_user.token)
    assert response.status_code == 201
    recipe_slug = response.json()

    response = api_client.get(api_routes.recipes_slug(recipe_slug), headers=unique_user.token)
    assert response.status_code == 200
    recipe = response.json()
    recipe["tags"] = created_tags

    response = api_client.put(api_routes.recipes_slug(recipe_slug), json=recipe, headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.get(TAGS_ROUTE, params={"perPage": -1}, headers=unique_user.token)
    assert response.status_code == 200
    all_tags = response.json()["items"]
    ordered_ids = [tag["id"] for tag in reversed(all_tags)]

    response = api_client.put(f"{TAGS_ROUTE}/order", json=ordered_ids, headers=unique_user.token)
    assert response.status_code == 200
    assert [tag["id"] for tag in response.json()] == ordered_ids
    assert [tag["position"] for tag in response.json()] == list(range(len(ordered_ids)))

    response = api_client.get(TAGS_ROUTE, params={"perPage": -1}, headers=unique_user.token)
    assert response.status_code == 200
    assert [tag["id"] for tag in response.json()["items"]] == ordered_ids

    response = api_client.get(api_routes.recipes_slug(recipe_slug), headers=unique_user.token)
    assert response.status_code == 200
    expected_recipe_tag_ids = [tag_id for tag_id in ordered_ids if tag_id in {tag["id"] for tag in created_tags}]
    assert [tag["id"] for tag in response.json()["tags"]] == expected_recipe_tag_ids

    response = api_client.get(api_routes.recipes, params={"perPage": -1}, headers=unique_user.token)
    assert response.status_code == 200
    recipe_summary = next(item for item in response.json()["items"] if item["slug"] == recipe_slug)
    assert [tag["id"] for tag in recipe_summary["tags"]] == expected_recipe_tag_ids


def test_update_tag_order_rejects_incomplete_list(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(TAGS_ROUTE, json={"name": random_string(10)}, headers=unique_user.token)
    assert response.status_code == 201

    response = api_client.put(f"{TAGS_ROUTE}/order", json=[], headers=unique_user.token)
    assert response.status_code == 400
