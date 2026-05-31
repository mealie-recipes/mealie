import pytest
import sqlalchemy as sa

from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.users.users import LongLiveToken, User
from mealie.services.query_filter.builder import (
    LogicalOperator,
    NonFilterableValueError,
    QueryFilterBuilder,
    QueryFilterJSON,
    QueryFilterJSONPart,
    RelationalKeyword,
    RelationalOperator,
)


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
# FilterableColumn tests
# ---------------------------------------------------------------------------


def test_non_filterable_field_user_password_raises():
    """Filtering on User.password (plain Mapped, not FilterableColumn) should raise ValueError."""
    with pytest.raises(NonFilterableValueError):
        QueryFilterBuilder.get_model_and_model_attr_from_attr_string("password", User)


def test_non_filterable_field_user_email_raises():
    """Filtering on User.email (plain Mapped, not FilterableColumn) should raise ValueError."""
    with pytest.raises(NonFilterableValueError):
        QueryFilterBuilder.get_model_and_model_attr_from_attr_string("email", User)


def test_non_filterable_field_long_live_token_raises():
    """Filtering on LongLiveToken.token (plain Mapped, not FilterableColumn) should raise ValueError."""
    with pytest.raises(NonFilterableValueError):
        QueryFilterBuilder.get_model_and_model_attr_from_attr_string("token", LongLiveToken)


def test_filterable_field_does_not_raise():
    """Filtering on a FilterableColumn field should not raise."""
    model, attr, _ = QueryFilterBuilder.get_model_and_model_attr_from_attr_string("full_name", User)
    assert model is User
    assert attr is User.full_name


# ---------------------------------------------------------------------------
# Relationship traversal tests
# ---------------------------------------------------------------------------


def test_deep_traversal_to_filterable_field_works():
    """Traversing a relationship to a FilterableColumn field should succeed."""
    model, attr, _ = QueryFilterBuilder.get_model_and_model_attr_from_attr_string("user.full_name", RecipeModel)
    assert model is User
    assert attr is User.full_name


def test_deep_traversal_to_non_filterable_field_raises():
    """Traversing a relationship to a plain Mapped field should raise ValueError."""
    with pytest.raises(NonFilterableValueError):
        QueryFilterBuilder.get_model_and_model_attr_from_attr_string("user.email", RecipeModel)


def test_deep_traversal_user_password_raises():
    """Traversing RecipeModel.user.password should raise ValueError."""
    with pytest.raises(NonFilterableValueError):
        QueryFilterBuilder.get_model_and_model_attr_from_attr_string("user.password", RecipeModel)


def test_filter_query_user_email_raises():
    """filter_query on user.email should raise ValueError."""
    query = sa.select(RecipeModel)
    builder = QueryFilterBuilder('user.email = "test@example.com"')
    with pytest.raises(NonFilterableValueError):
        builder.filter_query(query, RecipeModel)


def test_filter_query_user_password_raises():
    """filter_query on user.password should raise ValueError."""
    query = sa.select(RecipeModel)
    builder = QueryFilterBuilder('user.password = "secret"')
    with pytest.raises(NonFilterableValueError):
        builder.filter_query(query, RecipeModel)


def test_association_proxy_resolving_to_filterable_field_works():
    """Single-hop association proxy (e.g. household_id) resolving to a FilterableColumn should succeed."""
    model, attr, _ = QueryFilterBuilder.get_model_and_model_attr_from_attr_string("household_id", RecipeModel)
    assert model is User
    assert attr is User.household_id
