import re
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute, iter_route_contexts
from fastapi.testclient import TestClient

from mealie.app import app
from mealie.routes._base.permissions import Perm, RequirePermission
from mealie.schema.user.user import PrivateUser
from tests.utils.fixture_schemas import TestUser

# Every route that declares a permission, grouped by permission. A change here changes who can call a
# route, so it should be deliberate and visible in review.
EXPECTED_ROUTE_PERMISSIONS: dict[Perm, set[str]] = {
    Perm.GROUP_ORGANIZE: {
        "POST    /api/foods",
        "PUT     /api/foods/merge",
        "PUT     /api/foods/{item_id}",
        "DELETE  /api/foods/{item_id}",
        "POST    /api/groups/labels",
        "POST    /api/groups/labels/merge",
        "PUT     /api/groups/labels/{item_id}",
        "DELETE  /api/groups/labels/{item_id}",
        "POST    /api/groups/seeders/foods",
        "POST    /api/groups/seeders/units",
        "POST    /api/households/recipe-actions",
        "PUT     /api/households/recipe-actions/{item_id}",
        "DELETE  /api/households/recipe-actions/{item_id}",
        "POST    /api/organizers/categories",
        "POST    /api/organizers/categories/merge",
        "PUT     /api/organizers/categories/{item_id}",
        "DELETE  /api/organizers/categories/{item_id}",
        "POST    /api/organizers/tags",
        "POST    /api/organizers/tags/merge",
        "PUT     /api/organizers/tags/{item_id}",
        "DELETE  /api/organizers/tags/{item_id}",
        "POST    /api/organizers/tools",
        "POST    /api/organizers/tools/merge",
        "PUT     /api/organizers/tools/{item_id}",
        "DELETE  /api/organizers/tools/{item_id}",
        "POST    /api/units",
        "PUT     /api/units/merge",
        "PUT     /api/units/{item_id}",
        "DELETE  /api/units/{item_id}",
    },
    Perm.GROUP_MANAGE: {
        "POST    /api/groups/ai-providers/providers",
        "POST    /api/groups/ai-providers/providers/test",
        "GET     /api/groups/ai-providers/providers/{provider_id}",
        "PUT     /api/groups/ai-providers/providers/{provider_id}",
        "DELETE  /api/groups/ai-providers/providers/{provider_id}",
        "POST    /api/groups/ai-providers/providers/{provider_id}/test",
        "GET     /api/groups/ai-providers/prompts",
        "PUT     /api/groups/ai-providers/prompts/{prompt_name}",
        "DELETE  /api/groups/ai-providers/prompts/{prompt_name}",
        "GET     /api/groups/ai-providers/settings",
        "PUT     /api/groups/ai-providers/settings",
        "PUT     /api/groups/preferences",
        "GET     /api/households/members",
        "PUT     /api/households/permissions",
    },
    Perm.GROUP_INVITE: {
        "POST    /api/households/invitations",
        "POST    /api/households/invitations/email",
    },
    Perm.HOUSEHOLD_MANAGE: {
        "POST    /api/households/mealplans/ical",
        "DELETE  /api/households/mealplans/ical",
        "PUT     /api/households/preferences",
    },
}


def declared_route_permissions() -> dict[Perm, set[str]]:
    # FastAPI includes routers lazily, so `app.routes` holds the included routers rather than their routes.
    declared: dict[Perm, set[str]] = {}
    for route in iter_route_contexts(app.routes):
        if not isinstance(route.route, APIRoute):
            continue

        for dependency in route.dependant.dependencies:
            if isinstance(dependency.call, RequirePermission):
                for method in route.methods or ():
                    declared.setdefault(dependency.call.perm, set()).add(f"{method:<8}{route.path}")

    return declared


def test_routes_declare_expected_permissions():
    assert declared_route_permissions() == EXPECTED_ROUTE_PERMISSIONS


EXPECTED_ROUTES = sorted(route for routes in EXPECTED_ROUTE_PERMISSIONS.values() for route in routes)


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
