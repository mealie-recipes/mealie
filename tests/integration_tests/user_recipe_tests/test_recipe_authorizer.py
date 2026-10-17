import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.settings import RecipeSettings as RecipeSettingsModel
from mealie.repos.all_repositories import get_repositories
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_settings import RecipeSettings
from mealie.schema.user.user import PrivateUser
from mealie.services.authz.recipes import RecipePerm, RecipeAuthorizer
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

READ, UPDATE, DELETE = RecipePerm.READ, RecipePerm.UPDATE, RecipePerm.DELETE

# The recipe always belongs to `unique_user`. Each row: who acts, whether the recipe is locked, whether the
# owner's household locks edits from other households, and the actions that user may perform.
CASES = [
    ("owner", True, True, {READ, UPDATE, DELETE}),
    ("group_admin", True, True, {READ, UPDATE, DELETE}),
    ("same_household", False, True, {READ, UPDATE}),
    ("same_household", True, False, {READ}),
    ("other_household", False, False, {READ, UPDATE}),
    ("other_household", False, True, {READ}),
    ("other_household", True, False, {READ}),
    ("other_group", False, False, set()),
]


@pytest.fixture
def actors(
    unique_user: TestUser, unique_admin: TestUser, unprivileged_user: TestUser, h2_user: TestUser, g2_user: TestUser
) -> dict[str, TestUser]:
    return {
        "owner": unique_user,
        "group_admin": unique_admin,
        "same_household": unprivileged_user,
        "other_household": h2_user,
        "other_group": g2_user,
    }


def private_user(session: Session, user: TestUser) -> PrivateUser:
    # Unscoped, because `unique_admin` moved to another group after its repos were built.
    db_user = get_repositories(session, group_id=None, household_id=None).users.get_one(user.user_id)
    assert db_user
    return db_user


def create_recipe(owner: TestUser, locked: bool) -> Recipe:
    return owner.repos.recipes.create(
        Recipe(
            user_id=owner.user_id,
            group_id=owner.group_id,
            name=random_string(),
            settings=RecipeSettings(locked=locked),
        )
    )


def set_lock_other_households(owner: TestUser, value: bool) -> None:
    household = owner.repos.households.get_one(owner.household_id)
    assert household and household.preferences
    household.preferences.lock_recipe_edits_from_other_households = value
    owner.repos.household_preferences.update(household.id, household.preferences)


@pytest.mark.parametrize("actor, locked, lock_other_households, expected", CASES)
def test_recipe_rules(
    session: Session,
    unique_user: TestUser,
    actors: dict[str, TestUser],
    actor: str,
    locked: bool,
    lock_other_households: bool,
    expected: set[RecipePerm],
):
    set_lock_other_households(unique_user, lock_other_households)
    recipe = create_recipe(unique_user, locked)
    authorizer = RecipeAuthorizer(session, private_user(session, actors[actor]))

    granted = {action for action in RecipePerm if authorizer.allowed(action, [recipe.slug])}
    assert granted == expected


def test_recipe_without_settings_counts_as_locked(session: Session, unique_user: TestUser, unprivileged_user: TestUser):
    recipe = create_recipe(unique_user, locked=False)
    session.query(RecipeSettingsModel).filter_by(recipe_id=recipe.id).delete()
    session.commit()

    assert not RecipeAuthorizer(session, private_user(session, unprivileged_user)).allowed(UPDATE, [recipe.slug])


def test_allowed_needs_every_recipe(session: Session, unique_user: TestUser):
    authorizer = RecipeAuthorizer(session, private_user(session, unique_user))
    first, second = create_recipe(unique_user, False), create_recipe(unique_user, False)

    assert authorizer.allowed(DELETE, [first.slug, second.slug, first.slug])
    assert not authorizer.allowed(DELETE, [first.slug, random_string()])
    assert not authorizer.allowed(DELETE, [])


def test_clause_filters_list_queries(session: Session, unique_user: TestUser, unprivileged_user: TestUser):
    unlocked, locked = create_recipe(unique_user, False), create_recipe(unique_user, True)
    authorizer = RecipeAuthorizer(session, private_user(session, unprivileged_user))

    editable = set(
        session.scalars(
            sa.select(RecipeModel.slug).where(
                RecipeModel.slug.in_([unlocked.slug, locked.slug]), authorizer.clause(UPDATE)
            )
        )
    )
    assert editable == {unlocked.slug}


def test_household_rule_reads_the_owner_household(session: Session, unique_user: TestUser, h2_user: TestUser):
    # The two households disagree, so a rule that reads any household other than the owner's fails one side.
    set_lock_other_households(unique_user, True)
    set_lock_other_households(h2_user, False)
    unique_user_recipe, h2_recipe = create_recipe(unique_user, False), create_recipe(h2_user, False)

    assert RecipeAuthorizer(session, private_user(session, unique_user)).allowed(UPDATE, [h2_recipe.slug])
    assert not RecipeAuthorizer(session, private_user(session, h2_user)).allowed(UPDATE, [unique_user_recipe.slug])
