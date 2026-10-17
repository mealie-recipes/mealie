from collections.abc import Callable
from enum import StrEnum
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from mealie.core.dependencies import get_current_user
from mealie.db.db_setup import generate_session
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.schema.response import ErrorResponse
from mealie.schema.user.user import PrivateUser
from mealie.services.authz.recipes import RecipeAuthorizer, RecipePerm


class Perm(StrEnum):
    """
    A permission a route can require. The prefix names the scope the user flag applies to.
    `ANY_VALID_USER` marks a route as open to any signed-in user on purpose.
    """

    ANY_VALID_USER = "any_valid_user"
    GROUP_ORGANIZE = "group:organize"
    GROUP_MANAGE = "group:manage"
    GROUP_INVITE = "group:invite"
    HOUSEHOLD_MANAGE = "household:manage"


_GRANTED_BY: dict[Perm, Callable[[PrivateUser], bool]] = {
    Perm.ANY_VALID_USER: lambda _: True,
    Perm.GROUP_ORGANIZE: lambda user: user.can_organize,
    Perm.GROUP_MANAGE: lambda user: user.can_manage,
    Perm.HOUSEHOLD_MANAGE: lambda user: user.can_manage_household,
    Perm.GROUP_INVITE: lambda user: user.can_invite,
}


def forbidden(message: str | None = None) -> HTTPException:
    """The caller can see the resource but may not perform the action."""
    if message is None:
        return HTTPException(status.HTTP_403_FORBIDDEN)
    return HTTPException(status.HTTP_403_FORBIDDEN, detail=ErrorResponse.respond(message=message))


def not_found(message: str = "Not found.") -> HTTPException:
    """The caller cannot see the resource. Use it for missing and inaccessible resources alike."""
    return HTTPException(status.HTTP_404_NOT_FOUND, detail=ErrorResponse.respond(message=message))


class RouteRequirement:
    """
    Base class for route dependencies that gate access. The instance stays on the route's dependant, so
    the requirement each route declares can be read back from `app.routes` by its `label`.
    """

    label: str


class RequirePermission(RouteRequirement):
    """Route dependency that answers 403 unless the current user holds `perm`."""

    def __init__(self, perm: Perm) -> None:
        self.perm = perm
        self.label = perm

    def __call__(self, user: PrivateUser = Depends(get_current_user)) -> None:
        if not _GRANTED_BY[self.perm](user):
            raise forbidden()


def _matches_slug_or_id(slug_or_id: str) -> sa.ColumnElement[bool]:
    try:
        return RecipeModel.id == UUID(slug_or_id)
    except ValueError:
        return RecipeModel.slug == slug_or_id


class RequireRecipe(RouteRequirement):
    """
    Route dependency for the recipe named by the `{slug}` path parameter, which also accepts the recipe id.
    Answers 404 when the user cannot read the recipe and 403 when they do not hold `perm` on it.
    """

    def __init__(self, perm: RecipePerm) -> None:
        self.perm = perm
        self.label = perm

    def __call__(
        self,
        slug: str,
        user: PrivateUser = Depends(get_current_user),
        session: Session = Depends(generate_session),
    ) -> None:
        authorizer = RecipeAuthorizer(session, user)

        readable_slug = session.scalar(
            sa.select(RecipeModel.slug).where(_matches_slug_or_id(slug), authorizer.clause(RecipePerm.READ))
        )
        if readable_slug is None:
            raise not_found("No Entry Found")
        if not authorizer.allowed(self.perm, [readable_slug]):
            raise forbidden("Permission Denied")


def require(perm: Perm | RecipePerm) -> Any:
    """
    Declare what a route needs: `@router.post("", dependencies=[require(Perm.GROUP_ORGANIZE)])`. A `Perm` checks
    the user. A `RecipePerm` checks the recipe at `{slug}`, so the route path must have that parameter.
    """
    match perm:
        case Perm():
            return Depends(RequirePermission(perm))
        case RecipePerm():
            return Depends(RequireRecipe(perm))
