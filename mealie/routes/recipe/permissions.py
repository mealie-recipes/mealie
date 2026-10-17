from enum import StrEnum
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from mealie.core.dependencies import get_current_user
from mealie.core.exceptions import NoEntryFound
from mealie.db.db_setup import generate_session
from mealie.lang import get_locale_provider
from mealie.lang.providers import Translator
from mealie.repos.all_repositories import get_repositories
from mealie.routes._base.permissions import RouteRequirement, forbidden, not_found
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.user.user import PrivateUser
from mealie.services.recipe.recipe_service import RecipeService


class RecipeAction(StrEnum):
    UPDATE = "recipe:update"
    DELETE = "recipe:delete"


class RequireRecipe(RouteRequirement):
    """
    Route dependency that loads the recipe named by the `{slug}` path parameter from the user's group.
    Answers 404 when the user cannot see the recipe and 403 when they may not perform `action` on it.
    Returns the recipe, so a handler can take it as a parameter instead of loading it again.
    """

    def __init__(self, action: RecipeAction) -> None:
        self.action = action
        self.label = action

    def __call__(
        self,
        slug: str,
        user: PrivateUser = Depends(get_current_user),
        session: Session = Depends(generate_session),
        translator: Translator = Depends(get_locale_provider),
    ) -> Recipe:
        repos = get_repositories(session, group_id=user.group_id, household_id=user.household_id)
        service = RecipeService(repos, user, repos.households.get_one(user.household_id), translator)

        try:
            recipe = service.get_one(slug)
        except NoEntryFound:
            raise not_found("No Entry Found") from None

        match self.action:
            case RecipeAction.UPDATE:
                allowed = service.can_update([recipe.slug])
            case RecipeAction.DELETE:
                allowed = service.can_delete([recipe.slug])

        if not allowed:
            raise forbidden("Permission Denied")
        return recipe


def require_recipe(action: RecipeAction) -> Any:
    """Declare what a route does to the recipe at `{slug}`: `dependencies=[require_recipe(RecipeAction.UPDATE)]`."""
    return Depends(RequireRecipe(action))
