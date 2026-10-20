from datetime import UTC, datetime, timedelta

import pytest

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_share_token import RecipeShareToken, RecipeShareTokenSave
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
    assert db.recipes.get_one(recipe.slug)


def test_purge_expired_tokens_does_not_load_recipes(unique_user: TestUser, monkeypatch: pytest.MonkeyPatch) -> None:
    db = unique_user.repos
    recipe = db.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=random_string(20))
    )
    token = db.recipe_share_tokens.create(
        RecipeShareTokenSave(
            recipe_id=recipe.id, group_id=unique_user.group_id, expires_at=datetime.now(UTC) - timedelta(hours=1)
        )
    )

    def fail_loading_recipes() -> None:
        pytest.fail("Purging expired share tokens must not load or serialize their recipes")

    with monkeypatch.context() as patch:
        patch.setattr(RecipeShareToken, "loader_options", fail_loading_recipes)
        patch.setattr(RecipeShareToken, "model_validate", fail_loading_recipes)
        purge_expired_tokens()

    assert not db.recipe_share_tokens.get_one(token.id)
    assert db.recipes.get_one(recipe.slug)


def test_delete_expired_tokens_respects_group_and_expiry(unique_user: TestUser, g2_user: TestUser) -> None:
    current_time = datetime.now(UTC)
    tokens = []
    recipes = []
    for user in (unique_user, g2_user):
        recipe = user.repos.recipes.create(Recipe(user_id=user.user_id, group_id=user.group_id, name=random_string(20)))
        recipes.append(recipe)
        tokens.append(
            [
                user.repos.recipe_share_tokens.create(
                    RecipeShareTokenSave(recipe_id=recipe.id, group_id=user.group_id, expires_at=expires_at)
                )
                for expires_at in (current_time - timedelta(hours=1), current_time, current_time + timedelta(hours=1))
            ]
        )

    unique_user.repos.recipe_share_tokens.delete_expired(current_time)

    for user, user_tokens, recipe in zip((unique_user, g2_user), tokens, recipes, strict=True):
        for index, token in enumerate(user_tokens):
            exists = user.repos.recipe_share_tokens.get_one(token.id) is not None
            assert exists == (user is g2_user or index > 0)
        assert user.repos.recipes.get_one(recipe.slug)

    # The scheduler uses an unscoped repository, so all groups must be cleaned.
    purge_expired_tokens()
    for user, user_tokens, recipe in zip((unique_user, g2_user), tokens, recipes, strict=True):
        assert not user.repos.recipe_share_tokens.get_one(user_tokens[0].id)
        assert user.repos.recipe_share_tokens.get_one(user_tokens[2].id)
        assert user.repos.recipes.get_one(recipe.slug)
