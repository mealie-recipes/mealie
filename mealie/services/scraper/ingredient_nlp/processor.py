import subprocess
import tempfile
import unicodedata
from fractions import Fraction
from pathlib import Path
from typing import Optional

from mealie.core.config import settings
from mealie.schema.recipe import RecipeIngredient
from mealie.schema.recipe.recipe_ingredient import CreateIngredientFood, CreateIngredientUnit
from pydantic import BaseModel

from . import utils

CWD = Path(__file__).parent
MODEL_PATH = CWD / "model.crfmodel"

INGREDIENT_TEXT = [
    "2 tablespoons honey",
    "1/2 cup flour",
    "Black pepper, to taste",
    "2 cups of garlic finely chopped",
    "2 liters whole milk",
]


class CRFIngredient(BaseModel):
    input: Optional[str] = ""
    name: Optional[str] = ""
    other: Optional[str] = ""
    qty: Optional[str] = ""
    comment: Optional[str] = ""
    unit: Optional[str] = ""


def _exec_crf_test(input_text):
    with tempfile.NamedTemporaryFile(mode="w") as input_file:
        input_file.write(utils.export_data(input_text))
        input_file.flush()
        return subprocess.check_output(["crf_test", "--verbose=1", "--model", MODEL_PATH, input_file.name]).decode(
            "utf-8"
        )


def fraction_finder(string: str):
    # TODO: I'm not confident this works well enough for production needs some testing and/or refacorting
    for c in string:
        try:
            name = unicodedata.name(c)
        except ValueError:
            continue
        if name.startswith("VULGAR FRACTION"):
            normalized = unicodedata.normalize("NFKC", c)
            numerator, _slash, denominator = normalized.partition("⁄")
            text = f"{numerator}/{denominator}"
            return string.replace(c, text)

    return string


def convert_list_to_crf_model(list_of_ingrdeint_text: list[str]):
    crf_output = _exec_crf_test([fraction_finder(x) for x in list_of_ingrdeint_text])

    crf_models = [CRFIngredient(**ingredient) for ingredient in utils.import_data(crf_output.split("\n"))]

    for model in crf_models:
        print(model)

    return crf_models


def convert_crf_models_to_ingredients(crf_models: list[CRFIngredient]):
    return [
        RecipeIngredient(
            title="",
            note=crf_model.comment,
            unit=CreateIngredientUnit(name=crf_model.unit),
            food=CreateIngredientFood(name=crf_model.name),
            disable_amount=settings.RECIPE_DISABLE_AMOUNT,
            quantity=float(sum(Fraction(s) for s in crf_model.qty.split())),
        )
        for crf_model in crf_models
    ]


if __name__ == "__main__":
    crf_models = convert_list_to_crf_model(INGREDIENT_TEXT)
    ingredients = convert_crf_models_to_ingredients(crf_models)

    for ingredient in ingredients:
        print(ingredient)
