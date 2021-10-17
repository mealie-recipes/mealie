from abc import ABC, abstractmethod
from fractions import Fraction

from mealie.core.root_logger import get_logger
from mealie.schema.recipe import RecipeIngredient
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    CreateIngredientUnit,
    IngredientConfidence,
    ParsedIngredient,
    RegisteredParser,
)

from . import brute, crfpp

logger = get_logger(__name__)


class ABCIngredientParser(ABC):
    """
    Abstract class for ingredient parsers.
    """

    def parse_one(self, ingredient_string: str) -> ParsedIngredient:
        pass

    @abstractmethod
    def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        ...


class BruteForceParser(ABCIngredientParser):
    """
    Brute force ingredient parser.
    """

    def __init__(self) -> None:
        pass

    def parse_one(self, ingredient: str) -> ParsedIngredient:
        bfi = brute.parse(ingredient)

        return ParsedIngredient(
            input=ingredient,
            ingredient=RecipeIngredient(
                unit=CreateIngredientUnit(name=bfi.unit),
                food=CreateIngredientFood(name=bfi.food),
                disable_amount=False,
                quantity=bfi.amount,
                note=bfi.note,
            ),
        )

    def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        return [self.parse_one(ingredient) for ingredient in ingredients]


class NLPParser(ABCIngredientParser):
    """
    Class for CRFPP ingredient parsers.
    """

    def __init__(self) -> None:
        pass

    def _crf_to_ingredient(self, crf_model: crfpp.CRFIngredient) -> ParsedIngredient:
        ingredient = None

        try:
            ingredient = RecipeIngredient(
                title="",
                note=crf_model.comment,
                unit=CreateIngredientUnit(name=crf_model.unit),
                food=CreateIngredientFood(name=crf_model.name),
                disable_amount=False,
                quantity=float(sum(Fraction(s) for s in crf_model.qty.split())),
            )
        except Exception as e:
            logger.error(f"Failed to parse ingredient: {crf_model}: {e}")
            # TODO: Capture some sort of state for the user to see that an exception occured
            ingredient = RecipeIngredient(
                title="",
                note=crf_model.input,
            )

        return ParsedIngredient(
            input=crf_model.input,
            ingredient=ingredient,
            confidence=IngredientConfidence(
                quantity=crf_model.confidence.qty,
                food=crf_model.confidence.name,
                **crf_model.confidence.dict(),
            ),
        )

    def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        crf_models = crfpp.convert_list_to_crf_model(ingredients)
        return [self._crf_to_ingredient(crf_model) for crf_model in crf_models]


__registrar = {
    RegisteredParser.nlp: NLPParser,
    RegisteredParser.brute: BruteForceParser,
}


def get_parser(parser: RegisteredParser) -> ABCIngredientParser:
    """
    get_parser returns an ingrdeint parser based on the string enum value
    passed in.
    """
    return __registrar.get(parser, NLPParser)()
