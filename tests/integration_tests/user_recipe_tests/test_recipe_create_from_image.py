import json

import pytest
from fastapi.testclient import TestClient

from mealie.schema.openai.recipe import (
    OpenAIRecipe,
    OpenAIRecipeIngredient,
    OpenAIRecipeInstruction,
    OpenAIRecipeNotes,
)
from mealie.services.openai import OpenAIService
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


def test_openai_create_recipe_from_image(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    unique_user: TestUser,
    test_image_jpg: str,
):
    async def mock_get_response(self, prompt: str, message: str, *args, **kwargs) -> str | None:
        data = OpenAIRecipe(
            name=random_string(),
            description=random_string(),
            recipe_yield=random_string(),
            total_time=random_string(),
            prep_time=random_string(),
            perform_time=random_string(),
            ingredients=[OpenAIRecipeIngredient(text=random_string()) for _ in range(random_int(5, 10))],
            instructions=[OpenAIRecipeInstruction(text=random_string()) for _ in range(1, random_int(5, 10))],
            notes=[OpenAIRecipeNotes(text=random_string()) for _ in range(random_int(2, 5))],
        )
        return data.model_dump_json()

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)
    with open(test_image_jpg, "rb") as f:
        r = api_client.post(
            api_routes.recipes_create_image,
            files={"images": ("test_image_jpg.jpg", f, "image/jpeg")},
            data={"extension": "jpg"},
            headers=unique_user.token,
        )
    assert r.status_code == 201

    # since OpenAI is mocked, we don't need to validate the data, we just need to make sure a recipe is created,
    # and that it has an image
    slug: str = json.loads(r.text)
    r = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
    assert r.status_code == 200
    recipe_id = r.json()["id"]

    r = api_client.get(
        api_routes.media_recipes_recipe_id_images_file_name(recipe_id, "original.webp"), headers=unique_user.token
    )
    assert r.status_code == 200
