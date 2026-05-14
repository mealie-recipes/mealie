import pytest
import sqlalchemy as sa

from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.users.users import LongLiveToken, User
from mealie.services.query_filter.builder import (
    LogicalOperator,
    QueryFilterBuilder,
    QueryFilterJSON,
    QueryFilterJSONPart,
    RelationalKeyword,
    RelationalOperator,
)
from mealie.services.query_filter.context import allow_filter_restricted


def test_query_filter_builder_json():
    qf = (
        '(( (name = "my-recipe") AND is_active = TRUE) AND tags.name CONTAINS ALL ["tag1","tag2"]) '
        'OR (name="my-other-recipe" AND (count=1 OR count=2) )'
    )
    builder = QueryFilterBuilder(qf)
    assert builder.as_json_model() == QueryFilterJSON(
        parts=[
            QueryFilterJSONPart(
                left_parenthesis="(((",
                attribute_name="name",
                relational_operator=RelationalOperator.EQ,
                value="my-recipe",
                right_parenthesis=")",
            ),
            QueryFilterJSONPart(
                logical_operator=LogicalOperator.AND,
                attribute_name="is_active",
                relational_operator=RelationalOperator.EQ,
                value="TRUE",
                right_parenthesis=")",
            ),
            QueryFilterJSONPart(
                logical_operator=LogicalOperator.AND,
                attribute_name="tags.name",
                relational_operator=RelationalKeyword.CONTAINS_ALL,
                value=["tag1", "tag2"],
                right_parenthesis=")",
            ),
            QueryFilterJSONPart(
                logical_operator=LogicalOperator.OR,
                left_parenthesis="(",
                attribute_name="name",
                relational_operator=RelationalOperator.EQ,
                value="my-other-recipe",
            ),
            QueryFilterJSONPart(
                logical_operator=LogicalOperator.AND,
                left_parenthesis="(",
                attribute_name="count",
                relational_operator=RelationalOperator.EQ,
                value="1",
            ),
            QueryFilterJSONPart(
                logical_operator=LogicalOperator.OR,
                attribute_name="count",
                relational_operator=RelationalOperator.EQ,
                value="2",
                right_parenthesis="))",
            ),
        ]
    )


def test_query_filter_builder_json_uses_raw_value():
    qf = "last_made <= $NOW-30d"
    builder = QueryFilterBuilder(qf)
    assert builder.as_json_model() == QueryFilterJSON(
        parts=[
            QueryFilterJSONPart(
                attribute_name="last_made",
                relational_operator=RelationalOperator.LTE,
                value="$NOW-30d",
            ),
        ]
    )


# ---------------------------------------------------------------------------
# PrivateColumn tests
# ---------------------------------------------------------------------------


def test_private_field_user_password_raises():
    """Filtering on User.password (PrivateColumn) should raise ValueError."""
    with pytest.raises(ValueError, match="private field"):
        QueryFilterBuilder.get_model_and_model_attr_from_attr_string("password", User)


def test_private_field_long_live_token_raises():
    """Filtering on LongLiveToken.token (PrivateColumn) should raise ValueError."""
    with pytest.raises(ValueError, match="private field"):
        QueryFilterBuilder.get_model_and_model_attr_from_attr_string("token", LongLiveToken)


def test_non_private_field_does_not_raise():
    """Filtering on a normal field should not raise."""
    model, attr, _ = QueryFilterBuilder.get_model_and_model_attr_from_attr_string("full_name", User)
    assert model is User
    assert attr is User.full_name


# ---------------------------------------------------------------------------
# __filter_restricted__ traversal tests
# ---------------------------------------------------------------------------


def test_restricted_traversal_blocked_when_disallowed():
    """Traversing into User (restricted) via RecipeModel.user should raise when allow_restricted=False."""
    with pytest.raises(ValueError, match="restricted model"):
        QueryFilterBuilder.get_model_and_model_attr_from_attr_string("user.email", RecipeModel, allow_restricted=False)


def test_restricted_traversal_allowed_by_default():
    """Traversing into User via RecipeModel.user should succeed when allow_restricted=True (default)."""
    model, attr, _ = QueryFilterBuilder.get_model_and_model_attr_from_attr_string("user.email", RecipeModel)
    assert model is User
    assert attr is User.email


# ---------------------------------------------------------------------------
# ContextVar tests
# ---------------------------------------------------------------------------


def test_allow_filter_restricted_default_is_true():
    """The ContextVar default must be True so authenticated requests are unrestricted."""
    assert allow_filter_restricted.get() is True


def test_filter_query_respects_context_var_false(monkeypatch):
    """filter_query should block restricted traversal when the ContextVar is False."""
    allow_filter_restricted.set(False)
    try:
        query = sa.select(RecipeModel)
        builder = QueryFilterBuilder("user.email = 'test@example.com'")
        with pytest.raises(ValueError, match="restricted model"):
            builder.filter_query(query, RecipeModel)
    finally:
        allow_filter_restricted.set(True)


def test_filter_query_respects_context_var_true():
    """filter_query should allow restricted traversal when the ContextVar is True (default)."""
    allow_filter_restricted.set(True)
    query = sa.select(RecipeModel)
    builder = QueryFilterBuilder("user.email = 'test@example.com'")
    # Should not raise
    builder.filter_query(query, RecipeModel)


# ---------------------------------------------------------------------------
# orderBy restricted traversal tests
# ---------------------------------------------------------------------------


def test_order_by_restricted_traversal_blocked():
    """get_model_and_model_attr_from_attr_string with allow_restricted=False blocks orderBy into User."""
    with pytest.raises(ValueError, match="restricted model"):
        QueryFilterBuilder.get_model_and_model_attr_from_attr_string("user.email", RecipeModel, allow_restricted=False)


def test_order_by_private_field_blocked():
    """Ordering by a PrivateColumn field should always raise, regardless of allow_restricted."""
    with pytest.raises(ValueError, match="private field"):
        QueryFilterBuilder.get_model_and_model_attr_from_attr_string("password", User, allow_restricted=True)
