import json

import pytest

from mealie.schema.openai.general import OpenAIText
from mealie.schema.openai.recipe_ingredient import OpenAIIngredient, OpenAIIngredients


def test_parse_plain_json_object():
    payload = {"text": "hello"}
    result = OpenAIText.parse_openai_response(json.dumps(payload))
    assert result.text == "hello"


def test_parse_strips_null_characters():
    # Existing behavior: embedded nulls are removed before validation.
    result = OpenAIText.parse_openai_response('{"text": "hel\x00lo"}')
    assert result.text == "hello"


@pytest.mark.parametrize(
    "raw",
    [
        '```json\n{"text": "fenced"}\n```',
        '```\n{"text": "fenced"}\n```',
        '```JSON\n{"text": "fenced"}\n```',
    ],
)
def test_parse_strips_markdown_code_fences(raw: str):
    result = OpenAIText.parse_openai_response(raw)
    assert result.text == "fenced"


def test_parse_preserves_markdown_bold_inside_string_values():
    result = OpenAIText.parse_openai_response('{"text": "**bold** value"}')
    assert result.text == "**bold** value"


def test_parse_preserves_backticks_inside_string_values():
    result = OpenAIText.parse_openai_response('{"text": "use `code` here and **bold** too"}')
    assert result.text == "use `code` here and **bold** too"


def test_parse_preserves_fence_like_content_inside_string_values():
    raw = json.dumps({"text": "outer ```json fence``` inside value"})
    result = OpenAIText.parse_openai_response(raw)
    assert result.text == "outer ```json fence``` inside value"


def test_parse_extracts_json_object_surrounded_by_text():
    raw = 'Sure! Here you go:\n{"text": "extracted"}\nHope that helps.'
    result = OpenAIText.parse_openai_response(raw)
    assert result.text == "extracted"


def test_parse_extracts_json_array_surrounded_by_text():
    raw = (
        'Parsed ingredients:\n[{"food": "onion", "quantity": 1, "unit": null, "note": null, "substitutes": []}]\nDone.'
    )
    result = OpenAIIngredients.parse_openai_response(raw)
    assert len(result.ingredients) == 1
    assert result.ingredients[0].food == "onion"
    assert result.ingredients[0].quantity == 1


def test_parse_wraps_bare_json_array_into_list_field():
    # Local models often return [...] instead of {"ingredients": [...]}
    raw = json.dumps(
        [
            {
                "food": "garlic",
                "quantity": 2,
                "unit": "cloves",
                "note": "minced",
                "substitutes": [],
            }
        ]
    )
    result = OpenAIIngredients.parse_openai_response(raw)
    assert len(result.ingredients) == 1
    assert result.ingredients[0].food == "garlic"
    assert result.ingredients[0].unit == "cloves"
    assert result.ingredients[0].note == "minced"


def test_parse_bare_array_with_fences_and_surrounding_text():
    raw = (
        "Here is the list:\n"
        "```json\n"
        '[{"food": "tomato", "quantity": 3, "unit": null, "note": null, "substitutes": []}]\n'
        "```\n"
    )
    result = OpenAIIngredients.parse_openai_response(raw)
    assert len(result.ingredients) == 1
    assert result.ingredients[0].food == "tomato"
    assert result.ingredients[0].quantity == 3


def test_parse_none_or_empty_raises_or_fails_validation():
    # Empty preprocess yields "" which is not valid JSON for OpenAIText.
    with pytest.raises(Exception):
        OpenAIText.parse_openai_response(None)
    with pytest.raises(Exception):
        OpenAIText.parse_openai_response("")


def test_parse_ingredient_object_not_array():
    raw = json.dumps(
        {
            "quantity": 0.5,
            "unit": "cup",
            "food": "rice",
            "note": None,
            "substitutes": [],
        }
    )
    result = OpenAIIngredient.parse_openai_response(raw)
    assert result.food == "rice"
    assert result.quantity == 0.5
    assert result.unit == "cup"
