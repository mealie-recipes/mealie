
import pytest
from fastapi.testclient import TestClient
from tests.utils.fixture_schemas import TestUser
from tests.utils import api_routes
from tests.utils.factories import random_string

def test_patch_recipe_with_new_tag(api_client: TestClient, unique_user: TestUser):
    # 1. Create a recipe
    slug = random_string()
    api_client.post(api_routes.recipes, json={"name": slug}, headers=unique_user.token)
    
    # 2. Patch the recipe with a new tag (without group_id)
    new_tag_name = "new-tag-6802"
    patch_payload = {
        "tags": [{"name": new_tag_name, "slug": new_tag_name}]
    }
    
    response = api_client.patch(
        api_routes.recipes_slug(slug), 
        json=patch_payload, 
        headers=unique_user.token
    )
    
    # 3. Assert success (200 OK) instead of 500
    assert response.status_code == 200
    
    # 4. Verify tag was added
    data = response.json()
    assert len(data["tags"]) == 1
    assert data["tags"][0]["name"] == new_tag_name
