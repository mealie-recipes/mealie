from dataclasses import dataclass, field
from fractions import Fraction
from itertools import zip_longest

from ingredient_parser import parse_ingredient
from ingredient_parser.dataclasses import CompositeIngredientAmount, IngredientAmount
from ingredient_parser.dataclasses import ParsedIngredient as IngredientParserParsedIngredient
from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.core.root_logger import get_logger
from mealie.lang.providers import Translator
from mealie.schema.recipe import RecipeIngredient
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    CreateIngredientUnit,
    IngredientConfidence,
    IngredientFood,
    IngredientUnit,
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

    async def parse_one(self, ingredient_string: str) -> ParsedIngredient:
        bfi = brute.parse(ingredient_string, self)

        parsed_ingredient = ParsedIngredient(
            input=ingredient_string,
            ingredient=RecipeIngredient(
                unit=CreateIngredientUnit(name=bfi.unit),
                food=CreateIngredientFood(name=bfi.food),
                quantity=bfi.amount,
                note=bfi.note,
            ),
        )

        matched_ingredient = self.find_ingredient_match(parsed_ingredient)

        qty_conf = 1
        note_conf = 1

        unit_obj = matched_ingredient.ingredient.unit
        food_obj = matched_ingredient.ingredient.food

        unit_conf = 1 if bfi.unit is None or isinstance(unit_obj, IngredientUnit) else 0
        food_conf = 1 if bfi.food is None or isinstance(food_obj, IngredientFood) else 0

        avg_conf = (qty_conf + unit_conf + food_conf + note_conf) / 4

        matched_ingredient.confidence = IngredientConfidence(
            average=avg_conf,
            quantity=qty_conf,
            unit=unit_conf,
            food=food_conf,
            comment=note_conf,
        )

        return matched_ingredient

    async def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        return [await self.parse_one(ingredient) for ingredient in ingredients]


@dataclass
class _IngredientPart:
    qty: float = 0
    unit: str = ""
    food: str = ""
    extra_amounts: list[IngredientAmount] = field(default_factory=list)
    qty_conf: float = 0
    unit_conf: float = 0
    food_conf: float = 0

    @property
    def avg_conf(self) -> float:
        confs = [self.qty_conf, self.unit_conf, self.food_conf]
        return sum(confs) / len(confs)


class NLPParser(ABCIngredientParser):
    """
    Class for Ingredient Parser library
    """

    @classmethod
    def _extract_amount(cls, ingredient: IngredientParserParsedIngredient) -> IngredientAmount:
        if not (ingredient_amounts := ingredient.amount):
            return IngredientAmount(
                quantity=Fraction(0), quantity_max=Fraction(0), unit="", text="", confidence=0, starting_index=-1
            )

        ingredient_amount = ingredient_amounts[0]
        if isinstance(ingredient_amount, CompositeIngredientAmount):
            ingredient_amount = ingredient_amount.amounts[0]

        return ingredient_amount

    @classmethod
    def _extract_quantity(cls, ingredient_amount: IngredientAmount) -> tuple[float, float]:
        confidence = ingredient_amount.confidence

        if isinstance(ingredient_amount.quantity, str):
            qty = extract_quantity_from_string(ingredient_amount.quantity)[0]
        else:
            try:
                qty = float(ingredient_amount.quantity)
            except ValueError:
                qty = 0
                confidence = 0

        return qty, confidence

    @classmethod
    def _extract_unit(cls, ingredient_amount: IngredientAmount) -> tuple[str, float]:
        confidence = ingredient_amount.confidence
        unit = str(ingredient_amount.unit) if ingredient_amount.unit else ""
        return unit, confidence

    @classmethod
    def _extract_note(
        cls, ingredient: IngredientParserParsedIngredient, extra_amounts: list[IngredientAmount] | None = None
    ) -> tuple[str, float]:
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
        if ingredient.purpose:
            note_parts.append(ingredient.purpose.text)
            confidences.append(ingredient.purpose.confidence)

        # average confidence among all note parts
        confidence = sum(confidences) / len(confidences) if confidences else 0

        note = ", ".join(note_parts)
        note = note.replace("(", "").replace(")", "")

        # insert extra amounts to the front of the notes with parenthesis
        if extra_amounts:
            amt_part = "(" + ", ".join([amount.text for amount in extra_amounts]) + ")"
            note = " ".join(filter(None, [amt_part, note]))

        return note, confidence

    def _convert_ingredient(self, ingredient: IngredientParserParsedIngredient) -> ParsedIngredient:
        ing_parts: list[_IngredientPart] = []

        for amount, ing_name in zip_longest(ingredient.amount, ingredient.name, fillvalue=None):
            part = _IngredientPart()

            if amount:
                if isinstance(amount, CompositeIngredientAmount):
                    part.extra_amounts = list(amount.amounts[1:])
                    amount = amount.amounts[0]

                part.qty, part.qty_conf = self._extract_quantity(amount)
                part.unit, part.unit_conf = self._extract_unit(amount)

            if ing_name:
                part.food = ing_name.text
                part.food_conf = ing_name.confidence

            ing_parts.append(part)

        note, note_conf = self._extract_note(ingredient, ing_parts[0].extra_amounts if ing_parts else None)

        # Safeguard in case the parser outputs nothing
        if not ing_parts:
            ing_parts.append(_IngredientPart())

        # average confidence for components which were parsed
        # uses ing_parts[0] since this is the primary ingredient
        primary = ing_parts[0]
        confidences: list[float] = []

        if primary.qty:
            confidences.append(primary.qty_conf)
        if primary.unit:
            confidences.append(primary.unit_conf)
        if primary.food:
            confidences.append(primary.food_conf)
        if note:
            confidences.append(note_conf)
        if len(ing_parts) > 1:
            confidences.extend([part.avg_conf for part in ing_parts[1:]])

        recipe_ingredients: list[RecipeIngredient] = []
        for i, part in enumerate(ing_parts):
            if not i:
                ing_note = note
            elif part.extra_amounts:
                # TODO: handle extra amounts when we add support for them
                # For now, just add them as a note ("and amt_1, and amt_2, and ...")
                ing_note = ", ".join(self.t("recipe.and-amount", amount=a.text) for a in part.extra_amounts)
            else:
                ing_note = None
            recipe_ingredients.append(
                RecipeIngredient(
                    quantity=part.qty,
                    unit=CreateIngredientUnit(name=part.unit) if part.unit else None,
                    food=CreateIngredientFood(name=part.food) if part.food else None,
                    note=ing_note,
                )
            )

        primary_ingredient = recipe_ingredients[0]  # there will always be at least one recipe ingredient
        extra_ingredients = recipe_ingredients[1:] if len(recipe_ingredients) > 1 else []

        # TODO: handle extra ingredients when we support them
        # For now, just add them to the note ("or ing_1, or ing_2, or ...")
        if extra_ingredients:
            extras_note_parts = [
                self.t("recipe.or-ingredient", ingredient=extra_ing.display) for extra_ing in extra_ingredients
            ]
            extras_note = ", ".join(extras_note_parts)
            primary_ingredient.note = " ".join(filter(None, [extras_note, primary_ingredient.note]))

            # re-calculate display property since we modified the note
            primary_ingredient.display = primary_ingredient._format_display()

        parsed_ingredient = ParsedIngredient(
            input=ingredient.sentence,
            confidence=IngredientConfidence(
                average=(sum(confidences) / len(confidences)) if confidences else 0,
                quantity=primary.qty_conf,
                unit=primary.unit_conf,
                food=primary.food_conf,
                comment=note_conf,
            ),
            ingredient=primary_ingredient,
        )

        return self.find_ingredient_match(parsed_ingredient)

    async def parse_one(self, ingredient_string: str) -> ParsedIngredient:
        database_units = {}
        for ingredient_unit in self.data_matcher.units_by_id.values():
            if ingredient_unit.name:
                plural_name = ingredient_unit.plural_name or ingredient_unit.name
                database_units[plural_name] = ingredient_unit.name

            if ingredient_unit.abbreviation:
                plural_abbr = ingredient_unit.plural_abbreviation or ingredient_unit.abbreviation
                database_units[plural_abbr] = ingredient_unit.abbreviation

        parsed_ingredient = parse_ingredient(ingredient_string, custom_units=database_units)
        return self._convert_ingredient(parsed_ingredient)

    async def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        return [await self.parse_one(ingredient) for ingredient in ingredients]


__registrar: dict[RegisteredParser, type[ABCIngredientParser]] = {
    RegisteredParser.nlp: NLPParser,
    RegisteredParser.brute: BruteForceParser,
    RegisteredParser.openai: openai.OpenAIParser,
}


def get_parser(
    parser: RegisteredParser, group_id: UUID4, session: Session, translator: Translator
) -> ABCIngredientParser:
    """
    get_parser returns an ingrdeint parser based on the string enum value
    passed in.
    """
    return __registrar.get(parser, NLPParser)(group_id, session, translator)
