from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe import CreateRecipe
from tests import utils
from tests.utils.fixture_schemas import TestUser


def test_recipe_duplicate_detection_by_name_and_ingredients(api_client: TestClient, unique_user: TestUser):
    # 1. Create a base recipe
    recipe_name = f"Best Chocolate Chip Cookies {utils.random_string(6)}"
    create_payload = CreateRecipe(name=recipe_name)
    create_res = api_client.post(
        "/api/recipes",
        json=create_payload.model_dump(),
        headers=unique_user.token,
    )
    assert create_res.status_code == 201
    created_slug = create_res.json()

    # Get the created recipe to get its ID
    get_res = api_client.get(f"/api/recipes/{created_slug}", headers=unique_user.token)
    assert get_res.status_code == 200
    recipe_data = get_res.json()
    recipe_id = recipe_data["id"]

    # 2. Check duplicate with the exact same name
    check_payload = {
        "name": recipe_name,
        "ingredients": [
            {"name": "flour", "quantity": 2.0, "unit": "cups"},
            {"name": "chocolate chips", "quantity": 1.0, "unit": "cup"},
        ],
    }
    check_res = api_client.post(
        "/api/recipes/check-duplicate",
        json=check_payload,
        headers=unique_user.token,
    )
    assert check_res.status_code == 200
    result = check_res.json()
    is_dup = result.get("isDuplicate", result.get("is_duplicate"))
    assert is_dup is True
    assert len(result["matches"]) >= 1
    match = result["matches"][0]
    assert match["slug"] == created_slug
    reason = match.get("matchReason", match.get("match_reason", ""))
    assert "name" in reason.lower()

    # 3. Check duplicate excluding the existing recipe ID (self-check during edit)
    check_self_payload = {
        "recipe_id": recipe_id,
        "name": recipe_name,
    }
    check_self_res = api_client.post(
        "/api/recipes/check-duplicate",
        json=check_self_payload,
        headers=unique_user.token,
    )
    assert check_self_res.status_code == 200
    self_result = check_self_res.json()
    self_is_dup = self_result.get("isDuplicate", self_result.get("is_duplicate"))
    assert self_is_dup is False
    assert len(self_result["matches"]) == 0

    # 4. Check duplicate with a unique recipe name
    unique_payload = {
        "name": f"Completely Unique Spicy Ramen {utils.random_string(10)}",
        "ingredients": [{"name": "ramen noodles", "quantity": 1.0}],
    }
    unique_res = api_client.post(
        "/api/recipes/check-duplicate",
        json=unique_payload,
        headers=unique_user.token,
    )
    assert unique_res.status_code == 200
    unique_result = unique_res.json()
    unique_is_dup = unique_result.get("isDuplicate", unique_result.get("is_duplicate"))
    assert unique_is_dup is False
    assert len(unique_result["matches"]) == 0


def test_recipe_duplicate_detection_by_url(api_client: TestClient, unique_user: TestUser):
    # Create a recipe with an org_url
    recipe_name = f"Web Scraped Pasta {utils.random_string(6)}"
    test_url = f"https://example.com/recipes/pasta-{utils.random_string(6)}"
    create_payload = CreateRecipe(name=recipe_name)
    create_res = api_client.post(
        "/api/recipes",
        json=create_payload.model_dump(),
        headers=unique_user.token,
    )
    assert create_res.status_code == 201
    slug = create_res.json()

    # Update recipe with org_url
    get_res = api_client.get(f"/api/recipes/{slug}", headers=unique_user.token)
    recipe_data = get_res.json()
    recipe_data["orgURL"] = test_url
    update_res = api_client.put(
        f"/api/recipes/{slug}",
        json=recipe_data,
        headers=unique_user.token,
    )
    assert update_res.status_code == 200

    # Check duplicate with the exact URL
    check_url_res = api_client.post(
        "/api/recipes/check-duplicate",
        json={"url": test_url},
        headers=unique_user.token,
    )
    assert check_url_res.status_code == 200
    url_result = check_url_res.json()
    url_is_dup = url_result.get("isDuplicate", url_result.get("is_duplicate"))
    assert url_is_dup is True
    assert len(url_result["matches"]) >= 1
    assert url_result["matches"][0]["slug"] == slug
    url_reason = url_result["matches"][0].get("matchReason", url_result["matches"][0].get("match_reason", ""))
    assert "url" in url_reason.lower()

    # Check duplicate with URL with trailing slash
    check_slash_res = api_client.post(
        "/api/recipes/check-duplicate",
        json={"url": f"{test_url}/"},
        headers=unique_user.token,
    )
    assert check_slash_res.status_code == 200
    slash_result = check_slash_res.json()
    slash_is_dup = slash_result.get("isDuplicate", slash_result.get("is_duplicate"))
    assert slash_is_dup is True
    assert len(slash_result["matches"]) >= 1
