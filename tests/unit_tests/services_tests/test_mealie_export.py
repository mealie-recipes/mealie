import json

import pytest

from mealie.services.recipe.mealie_export import parse_mealie_export

SNAKE_DUMP = {
    "id": "0b1d6f2e-6a51-4a39-9d43-8c9d3c2a1f00",
    "group_id": "5e35879a-2e24-4fce-a601-0956dd698939",
    "slug": "garlic-rice",
    "name": "Garlic Rice",
    "recipe_ingredient": [{"reference_id": "a8f1c7f4-3a7e-4e0b-9f6a-2b1c0d9e8f71", "note": "1 cup rice"}],
    "recipe_instructions": [{"text": "Cook the rice."}],
}

CAMEL_DUMP = {
    "id": "0b1d6f2e-6a51-4a39-9d43-8c9d3c2a1f00",
    "groupId": "5e35879a-2e24-4fce-a601-0956dd698939",
    "slug": "garlic-rice",
    "name": "Garlic Rice",
    "recipeIngredient": [{"referenceId": "a8f1c7f4-3a7e-4e0b-9f6a-2b1c0d9e8f71", "note": "1 cup rice"}],
    "recipeInstructions": [{"text": "Cook the rice."}],
}


@pytest.mark.parametrize("dump", [SNAKE_DUMP, CAMEL_DUMP], ids=["snake_case", "camelCase"])
def test_recognises_complete_dump(dump: dict):
    assert parse_mealie_export(json.dumps(dump)) == dump


def test_recognises_dump_with_surrounding_whitespace():
    assert parse_mealie_export(f"\n  {json.dumps(CAMEL_DUMP)}  \n") == CAMEL_DUMP


@pytest.mark.parametrize(
    "data",
    [
        json.dumps({**CAMEL_DUMP, "@context": "https://schema.org", "@type": "Recipe"}),
        json.dumps({**CAMEL_DUMP, "@type": "Recipe"}),
        json.dumps({"name": "Test", "recipeIngredient": ["1 cup flour"], "recipeInstructions": [{"text": "Mix"}]}),
        json.dumps(
            {
                "name": "Loose",
                "recipeIngredient": [{"quantity": 1, "unit": {"name": "cup"}, "food": {"name": "rice"}}],
                "recipeInstructions": [{"summary": "Cook", "text": "Cook it."}],
            }
        ),
        json.dumps({k: v for k, v in CAMEL_DUMP.items() if k != "slug"}),
        json.dumps({**CAMEL_DUMP, "slug": "  "}),
        json.dumps({k: v for k, v in CAMEL_DUMP.items() if k != "groupId"}),
        json.dumps({**CAMEL_DUMP, "recipeIngredient": [{"note": "1 cup rice"}]}),
        json.dumps({**CAMEL_DUMP, "recipeIngredient": []}),
        json.dumps({**CAMEL_DUMP, "recipeIngredient": ["1 cup rice"]}),
        json.dumps([CAMEL_DUMP]),
        "<html><body>not a recipe</body></html>",
        '{"name": "Test",,,}',
        "",
    ],
    ids=[
        "schema-org",
        "type-only",
        "plain-json-string-lists",
        "loose-mealie-shaped",
        "no-slug",
        "blank-slug",
        "no-group-id",
        "ingredients-without-reference-ids",
        "no-ingredients",
        "string-ingredients",
        "json-array",
        "html",
        "malformed-json",
        "empty",
    ],
)
def test_ignores_anything_else(data: str):
    assert parse_mealie_export(data) is None
