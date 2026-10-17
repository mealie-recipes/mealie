import re
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute, iter_route_contexts
from fastapi.testclient import TestClient

from mealie.app import app
from mealie.routes._base.permissions import Perm, RequirePermission, RouteRequirement
from mealie.services.authz.recipes import RecipePerm
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_settings import RecipeSettings
from mealie.schema.user.user import PrivateUser
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

# Every route that declares a requirement, grouped by requirement. A change here changes who can call a
# route, so it should be deliberate and visible in review.
EXPECTED_ROUTE_REQUIREMENTS: dict[str, set[str]] = {
    Perm.GROUP_ORGANIZE: {
        "POST    /api/foods",
        "PUT     /api/foods/merge",
        "PUT     /api/foods/{item_id}",
        "DELETE  /api/foods/{item_id}",
        "POST    /api/groups/labels/merge",
        "POST    /api/organizers/categories",
        "POST    /api/organizers/categories/merge",
        "PUT     /api/organizers/categories/{item_id}",
        "DELETE  /api/organizers/categories/{item_id}",
        "POST    /api/organizers/tags",
        "POST    /api/organizers/tags/merge",
        "PUT     /api/organizers/tags/{item_id}",
        "DELETE  /api/organizers/tags/{item_id}",
        "POST    /api/organizers/tools/merge",
    },
    Perm.GROUP_MANAGE: {
        "POST    /api/groups/ai-providers/providers",
        "POST    /api/groups/ai-providers/providers/test",
        "GET     /api/groups/ai-providers/providers/{provider_id}",
        "PUT     /api/groups/ai-providers/providers/{provider_id}",
        "DELETE  /api/groups/ai-providers/providers/{provider_id}",
        "POST    /api/groups/ai-providers/providers/{provider_id}/test",
        "GET     /api/groups/ai-providers/settings",
        "PUT     /api/groups/ai-providers/settings",
        "PUT     /api/groups/preferences",
        "GET     /api/households/members",
        "PUT     /api/households/permissions",
    },
    Perm.HOUSEHOLD_MANAGE: {
        "POST    /api/households/mealplans/ical",
        "DELETE  /api/households/mealplans/ical",
        "PUT     /api/households/preferences",
    },
    RecipePerm.UPDATE: {
        "PUT     /api/recipes/{slug}",
        "PATCH   /api/recipes/{slug}",
        "PUT     /api/recipes/{slug}/image",
        "DELETE  /api/recipes/{slug}/image",
    },
    RecipePerm.DELETE: {
        "DELETE  /api/recipes/{slug}",
    },
}


def declared_route_requirements() -> dict[str, set[str]]:
    # FastAPI includes routers lazily, so `app.routes` holds the included routers rather than their routes.
    declared: dict[str, set[str]] = {}
    for route in iter_route_contexts(app.routes):
        if not isinstance(route.route, APIRoute):
            continue

        for dependency in route.dependant.dependencies:
            if isinstance(dependency.call, RouteRequirement):
                for method in route.methods or ():
                    declared.setdefault(dependency.call.label, set()).add(f"{method:<8}{route.path}")

    return declared


def test_routes_declare_expected_requirements():
    assert declared_route_requirements() == EXPECTED_ROUTE_REQUIREMENTS


# Only user permissions: a recipe requirement looks up the recipe first, so a random slug answers 404.
EXPECTED_ROUTES = sorted(
    route
    for requirement, routes in EXPECTED_ROUTE_REQUIREMENTS.items()
    if isinstance(requirement, Perm)
    for route in routes
)


def call_route(api_client: TestClient, route: str, user: TestUser):
    method, path = route.split()
    # Random ids and an empty body are enough: the permission check runs before FastAPI loads or validates
    # anything, so a caller without the permission gets 403 and any other status means the check passed.
    path = re.sub(r"{[^}]+}", lambda _: str(uuid4()), path)
    return api_client.request(method, path, json={}, headers=user.token)


@pytest.mark.parametrize("route", EXPECTED_ROUTES)
def test_route_rejects_user_without_permission(api_client: TestClient, unprivileged_user: TestUser, route: str):
    assert call_route(api_client, route, unprivileged_user).status_code == 403


@pytest.mark.parametrize("route", EXPECTED_ROUTES)
def test_route_allows_user_with_permission(api_client: TestClient, unique_user: TestUser, route: str):
    assert call_route(api_client, route, unique_user).status_code != 403


RECIPE_ROUTES = sorted(
    route
    for requirement, routes in EXPECTED_ROUTE_REQUIREMENTS.items()
    if isinstance(requirement, RecipePerm)
    for route in routes
)


@pytest.fixture(scope="module")
def locked_recipe(unique_user: TestUser) -> Recipe:
    return unique_user.repos.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=random_string(),
            settings=RecipeSettings(locked=True),
        )
    )


def call_recipe_route(api_client: TestClient, route: str, recipe: Recipe, user: TestUser):
    method, path = route.split()
    return api_client.request(method, path.replace("{slug}", recipe.slug), json={}, headers=user.token)


@pytest.mark.parametrize("route", RECIPE_ROUTES)
def test_recipe_route_rejects_other_user_on_locked_recipe(
    api_client: TestClient, unprivileged_user: TestUser, locked_recipe: Recipe, route: str
):
    assert call_recipe_route(api_client, route, locked_recipe, unprivileged_user).status_code == 403


@pytest.mark.parametrize("route", RECIPE_ROUTES)
def test_recipe_route_hides_recipe_from_other_group(
    api_client: TestClient, g2_user: TestUser, locked_recipe: Recipe, route: str
):
    assert call_recipe_route(api_client, route, locked_recipe, g2_user).status_code == 404


@pytest.mark.parametrize(
    "perm, flag",
    [
        (Perm.GROUP_ORGANIZE, "can_organize"),
        (Perm.GROUP_MANAGE, "can_manage"),
        (Perm.GROUP_INVITE, "can_invite"),
        (Perm.HOUSEHOLD_MANAGE, "can_manage_household"),
    ],
)
def test_require_permission_checks_user_flag(perm: Perm, flag: str):
    check = RequirePermission(perm)

    check(PrivateUser.model_construct(**{flag: True}))

    with pytest.raises(HTTPException) as exc_info:
        check(PrivateUser.model_construct(**{flag: False}))
    assert exc_info.value.status_code == 403


def test_require_any_valid_user_allows_any_user():
    RequirePermission(Perm.ANY_VALID_USER)(PrivateUser.model_construct())
