from ingredient_parser import parse_ingredient
from ingredient_parser.dataclasses import CompositeIngredientAmount, IngredientAmount
from ingredient_parser.dataclasses import ParsedIngredient as IngredientParserParsedIngredient
from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.core.root_logger import get_logger
from mealie.schema.recipe import RecipeIngredient
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    CreateIngredientUnit,
    IngredientConfidence,
    ParsedIngredient,
    RegisteredParser,
)

from . import brute, openai
from ._base import ABCIngredientParser
from .parser_utils import extract_quantity_from_string

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
    Class for Ingredient Parser library
    """

    @staticmethod
    def _extract_amount(ingredient: IngredientParserParsedIngredient) -> IngredientAmount:
        if not (ingredient_amounts := ingredient.amount):
            return IngredientAmount(quantity=0, quantity_max=0, unit="", text="", confidence=0, starting_index=-1)

        ingredient_amount = ingredient_amounts[0]
        if isinstance(ingredient_amount, CompositeIngredientAmount):
            ingredient_amount = ingredient_amount.amounts[0]

        return ingredient_amount

    @staticmethod
    def _extract_quantity(ingredient_amount: IngredientAmount) -> tuple[float, float]:
        confidence = ingredient_amount.confidence

        if isinstance(ingredient_amount.quantity, str):
            return extract_quantity_from_string(ingredient_amount.quantity)[0], confidence
        else:
            try:
                return float(ingredient_amount.quantity), confidence
            except ValueError:
                return 0, 0

    @staticmethod
    def _extract_unit(ingredient_amount: IngredientAmount) -> tuple[str, float]:
        confidence = ingredient_amount.confidence
        unit = str(ingredient_amount.unit) if ingredient_amount.unit else ""
        return unit, confidence

    @staticmethod
    def _extract_food(ingredient: IngredientParserParsedIngredient) -> tuple[str, float]:
        confidence = ingredient.name.confidence if ingredient.name else 0
        food = str(ingredient.name.text) if ingredient.name else ""
        return food, confidence

    @staticmethod
    def _extract_note(ingredient: IngredientParserParsedIngredient) -> tuple[str, float]:
        confidences: list[float] = []
        note_parts: list[str] = []
        if ingredient.size:
            note_parts.append(ingredient.size.text)
            confidences.append(ingredient.size.confidence)
        if ingredient.preparation:
            note_parts.append(ingredient.preparation.text)
            confidences.append(ingredient.preparation.confidence)
        if ingredient.comment:
            note_parts.append(ingredient.comment.text)
            confidences.append(ingredient.comment.confidence)

        # average confidence among all note parts
        confidence = sum(confidences) / len(confidences) if confidences else 0
        note = ", ".join(note_parts)
        note = note.replace("(", "").replace(")", "")

        return note, confidence

    def _convert_ingredient(self, ingredient: IngredientParserParsedIngredient) -> ParsedIngredient:
        ingredient_amount = self._extract_amount(ingredient)
        qty, qty_conf = self._extract_quantity(ingredient_amount)
        unit, unit_conf = self._extract_unit(ingredient_amount)
        food, food_conf = self._extract_food(ingredient)
        note, note_conf = self._extract_note(ingredient)

        # average confidence for components which were parsed
        confidences: list[float] = []
        if qty:
            confidences.append(qty_conf)
        if unit:
            confidences.append(unit_conf)
        if food:
            confidences.append(food_conf)
        if note:
            confidences.append(note_conf)

        parsed_ingredient = ParsedIngredient(
            input=ingredient.sentence,
            confidence=IngredientConfidence(
                average=(sum(confidences) / len(confidences)) if confidences else 0,
                quantity=qty_conf,
                unit=unit_conf,
                food=food_conf,
                comment=note_conf,
            ),
            ingredient=RecipeIngredient(
                title="",
                quantity=qty,
                unit=CreateIngredientUnit(name=unit) if unit else None,
                food=CreateIngredientFood(name=food) if food else None,
                disable_amount=False,
                note=note,
            ),
        )

        return self.find_ingredient_match(parsed_ingredient)

    async def parse_one(self, ingredient_string: str) -> ParsedIngredient:
        parsed_ingredient = parse_ingredient(ingredient_string)
        return self._convert_ingredient(parsed_ingredient)

    async def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        return [await self.parse_one(ingredient) for ingredient in ingredients]


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
