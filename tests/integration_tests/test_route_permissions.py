import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute, iter_route_contexts

from mealie.app import app
from mealie.routes._base.permissions import Perm, RequirePermission
from mealie.schema.user.user import PrivateUser

# Every route that declares a permission, grouped by permission. A change here changes who can call a
# route, so it should be deliberate and visible in review.
EXPECTED_ROUTE_PERMISSIONS: dict[Perm, set[str]] = {
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
        "GET     /api/groups/ai-providers/prompts",
        "PUT     /api/groups/ai-providers/prompts/{prompt_name}",
        "DELETE  /api/groups/ai-providers/prompts/{prompt_name}",
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
