from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import RecipeDraft, RecipeOut
from mealie.schema.recipe.recipe_settings import RecipeSettings
from mealie.services.recipe.recipe_service import RecipeDataService
from tests import data
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_ownership_on_new_with_admin(api_client: TestClient, admin_user: TestUser):
    recipe_name = random_string()
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=admin_user.token)
    assert response.status_code == 201

    recipe = api_client.get(api_routes.recipes + f"/{recipe_name}", headers=admin_user.token).json()

    assert recipe["userId"] == str(admin_user.user_id)
    assert recipe["groupId"] == str(admin_user.group_id)


def test_ownership_on_new_with_user(api_client: TestClient, g2_user: TestUser):
    recipe_name = random_string()
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=g2_user.token)
    assert response.status_code == 201

    response = api_client.get(api_routes.recipes + f"/{recipe_name}", headers=g2_user.token)

    assert response.status_code == 200

    recipe = response.json()

    assert recipe["userId"] == str(g2_user.user_id)
    assert recipe["groupId"] == str(g2_user.group_id)


def test_get_all_only_includes_group_recipes(api_client: TestClient, unique_user: TestUser):
    for _ in range(5):
        recipe_name = random_string()
        response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=unique_user.token)

    response = api_client.get(api_routes.recipes, headers=unique_user.token)

    assert response.status_code == 200

    recipes = response.json()["items"]

    assert len(recipes) == 5

    for recipe in recipes:
        assert recipe["groupId"] == str(unique_user.group_id)
        assert recipe["userId"] == str(unique_user.user_id)


def test_unique_slug_by_group(api_client: TestClient, unique_user: TestUser, g2_user: TestUser) -> None:
    create_data = {"name": random_string()}

    response = api_client.post(api_routes.recipes, json=create_data, headers=unique_user.token)
    assert response.status_code == 201

    response = api_client.post(api_routes.recipes, json=create_data, headers=g2_user.token)
    assert response.status_code == 201

    # Try to create a recipe again with the same name and check that the name was incremented
    response = api_client.post(api_routes.recipes, json=create_data, headers=g2_user.token)
    assert response.status_code == 201
    assert response.json() == create_data["name"] + "-1"


def test_user_locked_recipe(api_client: TestClient, user_tuple: list[TestUser]) -> None:
    usr_1, usr_2 = user_tuple

    # Setup Recipe
    recipe_name = random_string()
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=usr_1.token)
    assert response.status_code == 201

    # Get Recipe
    response = api_client.get(api_routes.recipes + f"/{recipe_name}", headers=usr_1.token)
    assert response.status_code == 200
    recipe = response.json()

    # Lock Recipe
    recipe["settings"]["locked"] = True
    response = api_client.put(api_routes.recipes + f"/{recipe_name}", json=recipe, headers=usr_1.token)

    # Try To Update Recipe with User 2
    response = api_client.put(api_routes.recipes + f"/{recipe_name}", json=recipe, headers=usr_2.token)
    assert response.status_code == 403


def test_user_update_last_made(api_client: TestClient, user_tuple: list[TestUser]) -> None:
    usr_1, usr_2 = user_tuple

    # Setup Recipe
    recipe_name = random_string()
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=usr_1.token)
    assert response.status_code == 201

    # Get Recipe
    response = api_client.get(api_routes.recipes + f"/{recipe_name}", headers=usr_1.token)
    assert response.status_code == 200
    recipe = response.json()

    # Lock Recipe
    recipe["settings"]["locked"] = True
    response = api_client.put(api_routes.recipes + f"/{recipe_name}", json=recipe, headers=usr_1.token)

    # User 2 should be able to update the last made timestamp
    last_made_json = {"timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z")}
    response = api_client.patch(
        api_routes.recipes_slug_last_made(recipe_name), json=last_made_json, headers=usr_2.token
    )
    assert response.status_code == 200

    response = api_client.get(api_routes.households_self_recipes_recipe_slug(recipe_name), headers=usr_2.token)
    assert response.status_code == 200
    assert response.json()["lastMade"] == last_made_json["timestamp"]

    earlier_last_made_json = {"timestamp": (datetime.now(UTC) - timedelta(days=1)).isoformat().replace("+00:00", "Z")}
    response = api_client.patch(
        api_routes.recipes_slug_last_made(recipe_name), json=earlier_last_made_json, headers=usr_2.token
    )
    assert response.status_code == 200

    response = api_client.get(api_routes.households_self_recipes_recipe_slug(recipe_name), headers=usr_2.token)
    assert response.status_code == 200
    assert response.json()["lastMade"] == earlier_last_made_json["timestamp"]

    response = api_client.get(api_routes.recipes + f"/{recipe_name}", headers=usr_1.token)
    assert response.status_code == 200
    assert "lastMade" not in response.json()


def test_other_user_cant_lock_recipe(api_client: TestClient, user_tuple: list[TestUser]) -> None:
    usr_1, usr_2 = user_tuple

    # Setup Recipe
    recipe_name = random_string()
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=usr_1.token)
    assert response.status_code == 201

    # Get Recipe
    response = api_client.get(api_routes.recipes + f"/{recipe_name}", headers=usr_2.token)
    assert response.status_code == 200
    recipe = response.json()

    # Lock Recipe
    recipe["settings"]["locked"] = True
    response = api_client.put(api_routes.recipes + f"/{recipe_name}", json=recipe, headers=usr_2.token)
    assert response.status_code == 403


def test_other_user_cant_delete_recipe(api_client: TestClient, user_tuple: list[TestUser]):
    slug = random_string(10)
    unique_user, other_user = user_tuple

    unique_user.repos.recipes.create(
        RecipeDraft(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug,
            settings=RecipeSettings(locked=True),
        )
    )

    response = api_client.delete(api_routes.recipes_slug(slug), headers=other_user.token)
    assert response.status_code == 403


def test_other_user_cant_delete_unlocked_recipe(api_client: TestClient, user_tuple: list[TestUser]):
    """Non-owner must not delete an unlocked recipe — BOLA regression (GHSA-x5v9-9jvh-7c7q)."""
    slug = random_string(10)
    unique_user, other_user = user_tuple

    unique_user.repos.recipes.create(
        RecipeDraft(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug,
            settings=RecipeSettings(locked=False),
        )
    )

    response = api_client.delete(api_routes.recipes_slug(slug), headers=other_user.token)
    assert response.status_code == 403


def test_other_user_bulk_delete(api_client: TestClient, user_tuple: list[TestUser]):
    slug_locked = random_string(10)
    slug_unlocked = random_string(10)
    unique_user, other_user = user_tuple

    unique_user.repos.recipes.create(
        RecipeDraft(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug_locked,
            settings=RecipeSettings(locked=True),
        )
    )
    unique_user.repos.recipes.create(
        RecipeDraft(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug_unlocked,
            settings=RecipeSettings(locked=False),
        )
    )

    response = api_client.post(
        api_routes.recipes_bulk_actions_delete,
        json={"recipes": [slug_locked, slug_unlocked]},
        headers=other_user.token,
    )
    assert response.status_code == 403


def test_other_user_cant_bulk_delete_unlocked_recipes(api_client: TestClient, user_tuple: list[TestUser]):
    """Non-owner must not bulk-delete unlocked recipes — BOLA regression (GHSA-x5v9-9jvh-7c7q)."""
    slug_1 = random_string(10)
    slug_2 = random_string(10)
    unique_user, other_user = user_tuple

    for slug in (slug_1, slug_2):
        unique_user.repos.recipes.create(
            RecipeDraft(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=slug,
                settings=RecipeSettings(locked=False),
            )
        )

    response = api_client.post(
        api_routes.recipes_bulk_actions_delete,
        json={"recipes": [slug_1, slug_2]},
        headers=other_user.token,
    )
    assert response.status_code == 403


def test_admin_can_delete_locked_recipe_owned_by_another_user(
    api_client: TestClient, unfiltered_database: AllRepositories, unique_user: TestUser, admin_user: TestUser
):
    slug = random_string(10)
    unique_user.repos.recipes.create(
        RecipeDraft(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=slug,
            settings=RecipeSettings(locked=True),
        )
    )

    # Make sure admin belongs to same group/household as user
    admin_data = unfiltered_database.users.get_one(admin_user.user_id)
    assert admin_data
    admin_data.group_id = UUID(unique_user.group_id)
    admin_data.household_id = UUID(unique_user.household_id)
    unfiltered_database.users.update(admin_user.user_id, admin_data)

    response = api_client.delete(api_routes.recipes_slug(slug), headers=admin_user.token)
    assert response.status_code == 200


def test_user_can_update_recipe_image(api_client: TestClient, unique_user: TestUser):
    data_payload = {"extension": "jpg"}
    file_payload = {"image": data.images_test_image_1.read_bytes()}

    household = unique_user.repos.households.get_one(unique_user.household_id)
    assert household and household.preferences
    household.preferences.private_household = True
    household.preferences.lock_recipe_edits_from_other_households = True
    unique_user.repos.household_preferences.update(household.id, household.preferences)

    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=unique_user.token)
    assert response.status_code == 201
    recipe_json = unique_user.repos.recipes.get_one(response.json())
    assert recipe_json and recipe_json.id
    assert recipe_json.image is None
    recipe_id = str(recipe_json.id)

    response = api_client.put(
        api_routes.recipes_slug_image(recipe_json.slug),
        data=data_payload,
        files=file_payload,
        headers=unique_user.token,
    )
    assert response.status_code == 200

    response = api_client.get(api_routes.recipes_slug(recipe_id), headers=unique_user.token)
    recipe_respons = response.json()
    assert recipe_respons["image"] is not None

    service = RecipeDataService(recipe_json.id)
    assert service.dir_image.exists() and any(f.is_file() for f in service.dir_image.iterdir())


def test_user_can_delete_recipe_image(api_client: TestClient, unique_user: TestUser):
    data_payload = {"extension": "jpg"}
    file_payload = {"image": data.images_test_image_1.read_bytes()}

    household = unique_user.repos.households.get_one(unique_user.household_id)
    assert household and household.preferences
    household.preferences.private_household = True
    household.preferences.lock_recipe_edits_from_other_households = True
    unique_user.repos.household_preferences.update(household.id, household.preferences)

    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=unique_user.token)
    assert response.status_code == 201
    recipe_json = unique_user.repos.recipes.get_one(response.json())
    assert recipe_json and recipe_json.id
    assert recipe_json.image is None
    recipe_id = str(recipe_json.id)

    response = api_client.put(
        api_routes.recipes_slug_image(recipe_json.slug),
        data=data_payload,
        files=file_payload,
        headers=unique_user.token,
    )
    assert response.status_code == 200

    response = api_client.get(api_routes.recipes_slug(recipe_id), headers=unique_user.token)
    recipe_respons = response.json()
    assert recipe_respons["image"] is not None

    service = RecipeDataService(recipe_json.id)
    assert service.dir_image.exists() and any(f.is_file() for f in service.dir_image.iterdir())

    response = api_client.delete(
        api_routes.recipes_slug_image(recipe_json.slug),
        headers=unique_user.token,
    )
    assert response.status_code == 200

    response = api_client.get(api_routes.recipes_slug(recipe_id), headers=unique_user.token)
    recipe_respons = response.json()
    assert recipe_respons["image"] is None
    assert not service.dir_image.exists() or not any(f.is_file() for f in service.dir_image.iterdir())


def _create_recipe(owner: TestUser, *, locked: bool) -> RecipeOut:
    return owner.repos.recipes.create(
        RecipeDraft(
            user_id=owner.user_id,
            group_id=owner.group_id,
            name=random_string(10),
            settings=RecipeSettings(locked=locked),
        )
    )


def _bulk_action_payloads(slug: str) -> list[tuple[str, dict]]:
    tag = {"id": str(uuid4()), "name": random_string(), "slug": random_string()}
    return [
        (api_routes.recipes_bulk_actions_tag, {"recipes": [slug], "tags": [tag]}),
        (api_routes.recipes_bulk_actions_categorize, {"recipes": [slug], "categories": [tag]}),
        (
            api_routes.recipes_bulk_actions_settings,
            {"recipes": [slug], "settings": RecipeSettings(public=True, show_nutrition=True).model_dump(by_alias=True)},
        ),
    ]


def _assert_recipe_unchanged(owner: TestUser, slug: str):
    recipe = owner.repos.recipes.get_one(slug)
    assert recipe and recipe.settings
    assert not recipe.tags
    assert not recipe.recipe_category
    assert not recipe.settings.public
    assert not recipe.settings.show_nutrition


def _recipe_locked_to_other_households(owner: TestUser) -> RecipeOut:
    household = owner.repos.households.get_one(owner.household_id)
    assert household and household.preferences
    household.preferences.lock_recipe_edits_from_other_households = True
    owner.repos.household_preferences.update(household.id, household.preferences)
    return _create_recipe(owner, locked=False)


def test_bulk_actions_reject_locked_recipe_of_other_user(api_client: TestClient, user_tuple: list[TestUser]):
    owner, other_user = user_tuple
    recipe = _create_recipe(owner, locked=True)

    for route, payload in _bulk_action_payloads(recipe.slug):
        response = api_client.post(route, json=payload, headers=other_user.token)
        assert response.status_code == 403, route
        _assert_recipe_unchanged(owner, recipe.slug)


def test_bulk_actions_reject_whole_set_when_one_recipe_is_locked(api_client: TestClient, user_tuple: list[TestUser]):
    owner, other_user = user_tuple
    open_recipe = _create_recipe(owner, locked=False)
    locked_recipe = _create_recipe(owner, locked=True)

    for route, payload in _bulk_action_payloads(open_recipe.slug):
        payload["recipes"] = [open_recipe.slug, locked_recipe.slug]
        response = api_client.post(route, json=payload, headers=other_user.token)
        assert response.status_code == 403, route
        _assert_recipe_unchanged(owner, open_recipe.slug)
        _assert_recipe_unchanged(owner, locked_recipe.slug)


@pytest.mark.parametrize("as_admin", [False, True])
def test_bulk_actions_reject_whole_set_when_one_recipe_is_missing(
    api_client: TestClient, unique_user: TestUser, unique_admin: TestUser, as_admin: bool
):
    recipe = _create_recipe(unique_user, locked=False)
    caller = unique_admin if as_admin else unique_user

    for route, payload in _bulk_action_payloads(recipe.slug):
        payload["recipes"] = [recipe.slug, random_string()]
        response = api_client.post(route, json=payload, headers=caller.token)
        assert response.status_code == 404, route
        _assert_recipe_unchanged(unique_user, recipe.slug)


def test_bulk_actions_accept_empty_set(api_client: TestClient, unique_user: TestUser):
    for route, payload in _bulk_action_payloads(random_string()):
        payload["recipes"] = []
        response = api_client.post(route, json=payload, headers=unique_user.token)
        assert response.status_code == 200, route


def test_bulk_actions_reject_recipe_of_locked_other_household(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser
):
    recipe = _recipe_locked_to_other_households(unique_user)

    for route, payload in _bulk_action_payloads(recipe.slug):
        response = api_client.post(route, json=payload, headers=h2_user.token)
        assert response.status_code == 403, route
        _assert_recipe_unchanged(unique_user, recipe.slug)


def test_bulk_actions_succeed_for_owner(api_client: TestClient, unique_user: TestUser):
    recipe = _create_recipe(unique_user, locked=True)

    for route, payload in _bulk_action_payloads(recipe.slug):
        response = api_client.post(route, json=payload, headers=unique_user.token)
        assert response.status_code == 200, route

    updated = unique_user.repos.recipes.get_one(recipe.slug)
    assert updated and updated.settings
    assert updated.tags
    assert updated.recipe_category
    assert updated.settings.public


def test_forbidden_image_url_scrape_downloads_nothing(
    api_client: TestClient, user_tuple: list[TestUser], monkeypatch: pytest.MonkeyPatch
):
    owner, other_user = user_tuple
    recipe = _create_recipe(owner, locked=True)
    downloads: list[str] = []

    async def record_download(self, url: str):
        downloads.append(url)

    monkeypatch.setattr(RecipeDataService, "scrape_image", record_download)

    response = api_client.post(
        api_routes.recipes_slug_image(recipe.slug), json={"url": "https://example.com/a.jpg"}, headers=other_user.token
    )
    assert response.status_code == 403
    assert not downloads
    unchanged = owner.repos.recipes.get_one(recipe.slug)
    assert unchanged and unchanged.image == recipe.image


def test_forbidden_image_upload_writes_nothing(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    recipe = _recipe_locked_to_other_households(unique_user)

    response = api_client.put(
        api_routes.recipes_slug_image(recipe.slug),
        data={"extension": "jpg"},
        files={"image": data.images_test_image_1.read_bytes()},
        headers=h2_user.token,
    )
    assert response.status_code == 403
    service = RecipeDataService(recipe.id)
    assert not any(f.is_file() for f in service.dir_data.rglob("*"))
    unchanged = unique_user.repos.recipes.get_one(recipe.slug)
    assert unchanged and unchanged.image == recipe.image


def test_forbidden_asset_upload_writes_nothing(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    recipe = _recipe_locked_to_other_households(unique_user)

    response = api_client.post(
        api_routes.recipes_slug_assets(recipe.slug),
        data={"name": "notes", "icon": "mdi-file", "extension": "txt"},
        files={"file": ("notes.txt", b"hello")},
        headers=h2_user.token,
    )
    assert response.status_code == 403
    assert not any(f.is_file() for f in recipe.asset_dir.rglob("*"))
    unchanged = unique_user.repos.recipes.get_one(recipe.slug)
    assert unchanged and not unchanged.assets


def test_forbidden_asset_from_url_downloads_nothing(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    recipe = _recipe_locked_to_other_households(unique_user)
    downloads: list[str] = []

    async def record_download(self, url: str, max_bytes: int):
        downloads.append(url)

    monkeypatch.setattr(RecipeDataService, "fetch_image", record_download)

    response = api_client.post(
        api_routes.recipes_slug_assets_url(recipe.slug),
        json={"url": "https://example.com/a.jpg"},
        headers=h2_user.token,
    )
    assert response.status_code == 403
    assert not downloads
    assert not any(f.is_file() for f in recipe.asset_dir.rglob("*"))


def test_owner_change_via_patch(api_client: TestClient, user_tuple: list[TestUser]):
    usr_1, usr_2 = user_tuple
    recipe = _create_recipe(usr_1, locked=False)

    response = api_client.patch(
        api_routes.recipes + f"/{recipe.slug}", json={"userId": str(usr_2.user_id)}, headers=usr_1.token
    )
    assert response.status_code == 200
    assert response.json()["userId"] == str(usr_2.user_id)

    updated = usr_1.repos.recipes.get_one(recipe.slug)
    assert updated is not None
    assert str(updated.user_id) == str(usr_2.user_id)
    assert str(updated.household_id) == str(usr_2.household_id)


def test_owner_change_via_put(api_client: TestClient, user_tuple: list[TestUser]):
    usr_1, usr_2 = user_tuple
    recipe = _create_recipe(usr_1, locked=False)

    # simulate the editor save: a full recipe round trip with the owner changed
    response = api_client.get(api_routes.recipes + f"/{recipe.slug}", headers=usr_1.token)
    assert response.status_code == 200
    recipe_json = response.json()
    recipe_json["userId"] = str(usr_2.user_id)

    response = api_client.put(api_routes.recipes + f"/{recipe.slug}", json=recipe_json, headers=usr_1.token)
    assert response.status_code == 200

    response = api_client.get(api_routes.recipes + f"/{recipe.slug}", headers=usr_2.token)
    assert response.status_code == 200
    assert response.json()["userId"] == str(usr_2.user_id)
    assert response.json()["householdId"] == str(usr_2.household_id)


def test_owner_change_moves_recipe_to_new_owner_household(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser
):
    recipe = _create_recipe(unique_user, locked=False)
    assert str(recipe.household_id) != str(h2_user.household_id)

    response = api_client.patch(
        api_routes.recipes + f"/{recipe.slug}", json={"userId": str(h2_user.user_id)}, headers=unique_user.token
    )
    assert response.status_code == 200

    # the recipe moved with the new owner, so the new owner can see it
    response = api_client.get(api_routes.recipes + f"/{recipe.slug}", headers=h2_user.token)
    assert response.status_code == 200
    assert response.json()["userId"] == str(h2_user.user_id)
    assert response.json()["householdId"] == str(h2_user.household_id)


def test_non_owner_cannot_change_owner(api_client: TestClient, user_tuple: list[TestUser]):
    usr_1, usr_2 = user_tuple
    recipe = _create_recipe(usr_1, locked=False)

    response = api_client.patch(
        api_routes.recipes + f"/{recipe.slug}", json={"userId": str(usr_2.user_id)}, headers=usr_2.token
    )
    assert response.status_code == 403

    unchanged = usr_1.repos.recipes.get_one(recipe.slug)
    assert unchanged is not None
    assert str(unchanged.user_id) == str(usr_1.user_id)
    assert str(unchanged.household_id) == str(usr_1.household_id)


def test_owner_change_rejects_user_of_other_group(api_client: TestClient, unique_user: TestUser, g2_user: TestUser):
    recipe = _create_recipe(unique_user, locked=False)

    response = api_client.patch(
        api_routes.recipes + f"/{recipe.slug}", json={"userId": str(g2_user.user_id)}, headers=unique_user.token
    )
    assert response.status_code == 404

    unchanged = unique_user.repos.recipes.get_one(recipe.slug)
    assert unchanged is not None
    assert str(unchanged.user_id) == str(unique_user.user_id)


def test_admin_can_change_owner(
    api_client: TestClient, unique_user: TestUser, unique_admin: TestUser, h2_user: TestUser
):
    recipe = _create_recipe(unique_user, locked=False)

    response = api_client.patch(
        api_routes.recipes + f"/{recipe.slug}", json={"userId": str(h2_user.user_id)}, headers=unique_admin.token
    )
    assert response.status_code == 200

    updated = h2_user.repos.recipes.get_one(recipe.slug)
    assert updated is not None
    assert str(updated.user_id) == str(h2_user.user_id)


def test_patch_with_null_user_id_keeps_owner(api_client: TestClient, user_tuple: list[TestUser]):
    usr_1, usr_2 = user_tuple
    recipe = _create_recipe(usr_1, locked=False)

    response = api_client.patch(api_routes.recipes + f"/{recipe.slug}", json={"userId": None}, headers=usr_2.token)
    assert response.status_code == 200

    unchanged = usr_1.repos.recipes.get_one(recipe.slug)
    assert unchanged is not None
    assert str(unchanged.user_id) == str(usr_1.user_id)
