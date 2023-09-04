from abc import ABC, abstractmethod
from fractions import Fraction

from fuzzywuzzy import fuzz
from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.core.root_logger import get_logger
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe import RecipeIngredient
from mealie.schema.recipe.recipe_ingredient import (
    MAX_INGREDIENT_DENOMINATOR,
    CreateIngredientFood,
    CreateIngredientUnit,
    IngredientConfidence,
    IngredientFood,
    IngredientUnit,
    ParsedIngredient,
    RegisteredParser,
)
from mealie.schema.response.pagination import PaginationQuery

from . import brute, crfpp

logger = get_logger(__name__)


class ABCIngredientParser(ABC):
    """
    Abstract class for ingredient parsers.
    """

    @property
    def _repos(self) -> AllRepositories:
        return get_repositories(self.session)

    @property
    def foods(self):
        return self._repos.ingredient_foods.by_group(self.group_id)

    @property
    def units(self):
        return self._repos.ingredient_units.by_group(self.group_id)

    @property
    def food_fuzzy_match_threshold(self) -> int:
        """Minimum threshold to fuzzy match against a database food search"""

        return 85

    @property
    def unit_fuzzy_match_threshold(self) -> int:
        """Minimum threshold to fuzzy match against a database unit search"""

        return 50

    def __init__(self, group_id: UUID4, session: Session) -> None:
        self.group_id = group_id
        self.session = session

    @abstractmethod
    def parse_one(self, ingredient_string: str) -> ParsedIngredient:
        ...

    @abstractmethod
    def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        ...

    def find_food_match(self, food: IngredientFood | CreateIngredientFood) -> IngredientFood | None:
        if isinstance(food, IngredientFood):
            return food

        query = PaginationQuery(page=1, per_page=10)
        response = self.foods.page_all(query, search=food.name)
        if not response.items:
            return None

        # further refine match using fuzzy matching
        best_match: IngredientFood | None = None
        best_match_score: int = 0

        for item in response.items:
            score = fuzz.ratio(food.name, item.name)
            if score == 100:
                return item
            elif score > best_match_score and score >= self.food_fuzzy_match_threshold:
                best_match = item
                best_match_score = score

        return best_match

    def find_unit_match(self, unit: IngredientUnit | CreateIngredientUnit) -> IngredientUnit | None:
        if isinstance(unit, IngredientUnit):
            return unit

        query = PaginationQuery(page=1, per_page=10)
        response = self.units.page_all(query, search=unit.name)
        if not response.items:
            return None

        # further refine match using fuzzy matching
        best_match: IngredientUnit | None = None
        best_match_score: int = 0

        for item in response.items:
            score = fuzz.ratio(unit.name, item.name)
            if score == 100:
                return item
            elif score > best_match_score and score >= self.unit_fuzzy_match_threshold:
                best_match = item
                best_match_score = score

        return best_match

    def find_ingredient_match(self, ingredient: ParsedIngredient) -> ParsedIngredient:
        if ingredient.ingredient.food and (food_match := self.find_food_match(ingredient.ingredient.food)):
            ingredient.ingredient.food = food_match

        if ingredient.ingredient.unit and (unit_match := self.find_unit_match(ingredient.ingredient.unit)):
            ingredient.ingredient.unit = unit_match

        return ingredient


class BruteForceParser(ABCIngredientParser):
    """
    Brute force ingredient parser.
    """

    def parse_one(self, ingredient: str) -> ParsedIngredient:
        bfi = brute.parse(ingredient)

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

    def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        return [self.parse_one(ingredient) for ingredient in ingredients]


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
                **crf_model.confidence.dict(),
            ),
        )

        return self.find_ingredient_match(parsed_ingredient)

    def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        crf_models = crfpp.convert_list_to_crf_model(ingredients)
        return [self._crf_to_ingredient(crf_model) for crf_model in crf_models]

    def parse_one(self, ingredient: str) -> ParsedIngredient:
        items = self.parse([ingredient])
        return items[0]


__registrar = {
    RegisteredParser.nlp: NLPParser,
    RegisteredParser.brute: BruteForceParser,
}


def get_parser(parser: RegisteredParser, group_id: UUID4, session: Session) -> ABCIngredientParser:
    """
    get_parser returns an ingrdeint parser based on the string enum value
    passed in.
    """
    return __registrar.get(parser, NLPParser)(group_id, session)
