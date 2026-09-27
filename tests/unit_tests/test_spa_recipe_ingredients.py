import json

import pytest
from bs4 import BeautifulSoup

from mealie.routes import spa
from mealie.schema.recipe.recipe import Recipe


@pytest.mark.parametrize(
    "ingredient, expected",
    [
        (
            {
                "quantity": 2.5,
                "unit": {"name": "Deziliter", "abbreviation": "dl", "useAbbreviation": True},
                "food": {"name": "Milch"},
            },
            "2.5 dl Milch",
        ),
        (
            {
                "quantity": 200,
                "unit": {"name": "Gramm", "abbreviation": "g", "useAbbreviation": True},
                "food": {"name": "Lauch"},
                "note": "in feinen Streifen",
            },
            "200 g Lauch, in feinen Streifen",
        ),
        ({"quantity": 2, "food": {"name": "Ei"}}, "2 Ei"),
        ({"quantity": 0.5, "unit": {"name": "cup", "fraction": True}, "food": {"name": "milk"}}, "0.5 cup milk"),
        ({"quantity": 2, "unit": {"name": "cup", "pluralName": "cups"}, "food": {"name": "milk"}}, "2 cups milk"),
        (
            {
                "quantity": 2,
                "unit": {
                    "name": "tablespoon",
                    "abbreviation": "tbsp",
                    "pluralAbbreviation": "tbsps",
                    "useAbbreviation": True,
                },
            },
            "2 tbsps",
        ),
        ({"quantity": 1, "unit": {"name": "cup", "useAbbreviation": True}, "food": {"name": "milk"}}, "1 cup milk"),
        ({"food": {"name": "Pfeffer"}}, "Pfeffer"),
        ({"note": "salt to taste"}, "salt to taste"),
        ({}, ""),
    ],
)
def test_recipe_ingredient_jsonld(ingredient: dict, expected: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(spa, "__contents", "<html><head></head><body></body></html>")
    recipe = Recipe.model_validate({"name": "Test recipe", "recipeIngredient": [ingredient]})

    soup = BeautifulSoup(spa.content_with_meta("home", recipe), "html.parser")
    script = soup.find("script", type="application/ld+json")
    assert script is not None
    assert json.loads(script.text)["recipeIngredient"] == [expected]
