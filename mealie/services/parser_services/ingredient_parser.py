from fractions import Fraction

from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.core.root_logger import get_logger
from mealie.schema.recipe import RecipeIngredient
from mealie.schema.recipe.recipe_ingredient import (
    MAX_INGREDIENT_DENOMINATOR,
    CreateIngredientFood,
    CreateIngredientUnit,
    IngredientConfidence,
    ParsedIngredient,
    RegisteredParser,
)

from . import brute, crfpp, openai
from ._base import ABCIngredientParser

logger = get_logger(__name__)


class BruteForceParser(ABCIngredientParser):
    """
    Brute force ingredient parser.
    """

    async def parse_one(self, ingredient: str) -> ParsedIngredient:
        bfi = brute.parse(ingredient, self)

        parsed_ingredient = ParsedIngredient(
            input=ingredient,
            ingredient=RecipeIngredient(
                unit=CreateIngredientUnit(name=bfi.unit),
                food=CreateIngredientFood(name=bfi.food),
                disable_amount=False,
                quantity=bfi.amount,
                note=bfi.note,
            ),
        )

        return self.find_ingredient_match(parsed_ingredient)

    async def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        return [await self.parse_one(ingredient) for ingredient in ingredients]


class NLPParser(ABCIngredientParser):
    """
    Class for CRFPP ingredient parsers.
    """

    def _crf_to_ingredient(self, crf_model: crfpp.CRFIngredient) -> ParsedIngredient:
        ingredient = None

        try:
            ingredient = RecipeIngredient(
                title="",
                note=crf_model.comment,
                unit=CreateIngredientUnit(name=crf_model.unit),
                food=CreateIngredientFood(name=crf_model.name),
                disable_amount=False,
                quantity=float(
                    sum(Fraction(s).limit_denominator(MAX_INGREDIENT_DENOMINATOR) for s in crf_model.qty.split())
                ),
            )
        except Exception as e:
            logger.error(f"Failed to parse ingredient: {crf_model}: {e}")
            # TODO: Capture some sort of state for the user to see that an exception occurred
            ingredient = RecipeIngredient(
                title="",
                note=crf_model.input,
            )

        parsed_ingredient = ParsedIngredient(
            input=crf_model.input,
            ingredient=ingredient,
            confidence=IngredientConfidence(
                quantity=crf_model.confidence.qty,
                food=crf_model.confidence.name,
                **crf_model.confidence.model_dump(),
            ),
        )

        return self.find_ingredient_match(parsed_ingredient)

    async def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        crf_models = crfpp.convert_list_to_crf_model(ingredients)
        return [self._crf_to_ingredient(crf_model) for crf_model in crf_models]

    async def parse_one(self, ingredient_string: str) -> ParsedIngredient:
        items = await self.parse([ingredient_string])
        return items[0]


__registrar: dict[RegisteredParser, type[ABCIngredientParser]] = {
    RegisteredParser.nlp: NLPParser,
    RegisteredParser.brute: BruteForceParser,
    RegisteredParser.openai: openai.OpenAIParser,
}


def get_parser(parser: RegisteredParser, group_id: UUID4, session: Session) -> ABCIngredientParser:
    """
    get_parser returns an ingrdeint parser based on the string enum value
    passed in.
    """
    return __registrar.get(parser, NLPParser)(group_id, session)
