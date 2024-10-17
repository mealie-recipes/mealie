from mealie.schema.response.query_filter import (
    LogicalOperator,
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
