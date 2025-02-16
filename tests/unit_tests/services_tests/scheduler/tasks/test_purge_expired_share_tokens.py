from datetime import UTC, datetime, timedelta

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_share_token import RecipeShareTokenSave
from mealie.services.scheduler.tasks.purge_expired_share_tokens import purge_expired_tokens
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_no_expired_tokens():
    # make sure this task runs successfully even if there are no expired tokens
    purge_expired_tokens()


def test_delete_expired_tokens(unique_user: TestUser):
    db = unique_user.repos
    recipe = db.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=random_string(20))
    )
    assert recipe and recipe.id
    good_token = db.recipe_share_tokens.create(
        RecipeShareTokenSave(
            recipe_id=recipe.id, group_id=unique_user.group_id, expires_at=datetime.now(UTC) + timedelta(hours=1)
        )
    )
    bad_token = db.recipe_share_tokens.create(
        RecipeShareTokenSave(
            recipe_id=recipe.id, group_id=unique_user.group_id, expires_at=datetime.now(UTC) - timedelta(hours=1)
        )
    )

    assert db.recipe_share_tokens.get_one(good_token.id)
    assert db.recipe_share_tokens.get_one(bad_token.id)

    purge_expired_tokens()

    assert db.recipe_share_tokens.get_one(good_token.id)
    assert not db.recipe_share_tokens.get_one(bad_token.id)
