"""
What anonymous users can see through the explore routes.

Pass these clauses to the repo as `extra_filter`. Don't append them to the request's
queryFilter: quotes or brackets in that string can swallow whatever follows.
"""

from typing import TypeGuard

import sqlalchemy as sa

from mealie.db.models.household import CookBook, Household, HouseholdPreferencesModel
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.settings import RecipeSettings
from mealie.db.models.users.users import User
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.household.household import HouseholdInDB
from mealie.schema.recipe.recipe import Recipe


def _household_is_public() -> sa.ColumnElement[bool]:
    return Household.preferences.has(HouseholdPreferencesModel.private_household.is_(False))


def public_households_clause() -> sa.ColumnElement[bool]:
    return _household_is_public()


def public_recipes_clause() -> sa.ColumnElement[bool]:
    return sa.and_(
        RecipeModel.settings.has(RecipeSettings.public.is_(True)),
        RecipeModel.user.has(User.household.has(_household_is_public())),
    )


def public_cookbooks_clause() -> sa.ColumnElement[bool]:
    return sa.and_(CookBook.public.is_(True), CookBook.household.has(_household_is_public()))


def is_household_publicly_visible(household: HouseholdInDB | None) -> bool:
    return bool(household and household.preferences and not household.preferences.private_household)


def is_recipe_publicly_visible(recipe: Recipe | None, household: HouseholdInDB | None) -> TypeGuard[Recipe]:
    return bool(recipe and recipe.settings and recipe.settings.public and is_household_publicly_visible(household))


def is_cookbook_publicly_visible(cookbook: ReadCookBook | None, household: HouseholdInDB | None) -> bool:
    return bool(cookbook and cookbook.public and is_household_publicly_visible(household))
