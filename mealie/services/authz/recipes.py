from collections.abc import Iterable
from enum import StrEnum

import sqlalchemy as sa
from sqlalchemy.orm import Session

from mealie.db.models.household.preferences import HouseholdPreferencesModel
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.settings import RecipeSettings
from mealie.db.models.users.users import User
from mealie.schema.user.user import PrivateUser


class RecipePerm(StrEnum):
    READ = "recipe:read"
    UPDATE = "recipe:update"
    DELETE = "recipe:delete"


class RecipeAuthorizer:
    """
    Decides which recipes a user may act on. Each rule is a SQL clause on `RecipeModel`, so list queries
    filter with the same rule that single-recipe and bulk checks use.
    """

    def __init__(self, session: Session, user: PrivateUser) -> None:
        self.session = session
        self.user = user

    def clause(self, perm: RecipePerm) -> sa.ColumnElement[bool]:
        """WHERE clause that matches the recipes the user may perform `perm` on."""
        in_group = RecipeModel.group_id == self.user.group_id
        if perm is RecipePerm.READ or self.user.admin:
            return in_group

        owned = RecipeModel.user_id == self.user.id
        match perm:
            case RecipePerm.UPDATE:
                return sa.and_(in_group, sa.or_(owned, self._editable_by_others()))
            case RecipePerm.DELETE:
                # Deletion requires ownership; the lock and household rules for edits do not apply.
                return sa.and_(in_group, owned)

    def allowed(self, perm: RecipePerm, slugs: Iterable[str]) -> bool:
        """True when every recipe in `slugs` exists in the user's group and passes `clause(perm)`."""
        unique_slugs = set(slugs)
        if not unique_slugs:
            return False

        matched = self.session.scalar(
            sa.select(sa.func.count())
            .select_from(RecipeModel)
            .where(RecipeModel.slug.in_(unique_slugs), self.clause(perm))
        )
        return matched == len(unique_slugs)

    def _editable_by_others(self) -> sa.ColumnElement[bool]:
        # A recipe with no settings row counts as locked, and an owner household with no preferences row
        # counts as locking edits from other households. A recipe with no owner household is not "other".
        locked = sa.select(RecipeSettings.locked).where(RecipeSettings.recipe_id == RecipeModel.id).scalar_subquery()
        owner_household_id = sa.select(User.household_id).where(User.id == RecipeModel.user_id).scalar_subquery()
        locks_other_households = (
            sa.select(HouseholdPreferencesModel.lock_recipe_edits_from_other_households)
            .join(User, User.household_id == HouseholdPreferencesModel.household_id)
            .where(User.id == RecipeModel.user_id)
            .scalar_subquery()
        )
        blocked_for_other_household = sa.and_(
            owner_household_id != self.user.household_id, sa.func.coalesce(locks_other_households, True)
        )

        return sa.and_(
            sa.not_(sa.func.coalesce(locked, True)),
            sa.not_(sa.func.coalesce(blocked_for_other_household, False)),
        )
