from abc import ABC, abstractmethod
from fractions import Fraction
from typing import TypeVar

from pydantic import UUID4, BaseModel
from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session

from mealie.core.root_logger import get_logger
from mealie.db.models.recipe.ingredient import IngredientFoodModel, IngredientUnitModel
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
T = TypeVar("T", bound=BaseModel)


class ABCIngredientParser(ABC):
    """
    Abstract class for ingredient parsers.
    """

    def __init__(self, group_id: UUID4, session: Session) -> None:
        self.group_id = group_id
        self.session = session

        self._foods_by_alias: dict[str, IngredientFood] | None = None
        self._units_by_alias: dict[str, IngredientUnit] | None = None

    @property
    def _repos(self) -> AllRepositories:
        return get_repositories(self.session)

    @property
    def foods_by_alias(self) -> dict[str, IngredientFood]:
        if self._foods_by_alias is None:
            foods_repo = self._repos.ingredient_foods.by_group(self.group_id)
            query = PaginationQuery(page=1, per_page=-1)
            all_foods = foods_repo.page_all(query).items

            foods_by_alias: dict[str, IngredientFood] = {}
            for food in all_foods:
                if food.name:
                    foods_by_alias[IngredientFoodModel.normalize(food.name)] = food
                if food.plural_name:
                    foods_by_alias[IngredientFoodModel.normalize(food.plural_name)] = food

                for alias in food.aliases or []:
                    if alias.name:
                        foods_by_alias[IngredientFoodModel.normalize(alias.name)] = food

            self._foods_by_alias = foods_by_alias

        return self._foods_by_alias

    @property
    def units_by_alias(self) -> dict[str, IngredientUnit]:
        if self._units_by_alias is None:
            units_repo = self._repos.ingredient_units.by_group(self.group_id)
            query = PaginationQuery(page=1, per_page=-1)
            all_units = units_repo.page_all(query).items

            units_by_alias: dict[str, IngredientUnit] = {}
            for unit in all_units:
                if unit.name:
                    units_by_alias[IngredientUnitModel.normalize(unit.name)] = unit
                if unit.plural_name:
                    units_by_alias[IngredientUnitModel.normalize(unit.plural_name)] = unit
                if unit.abbreviation:
                    units_by_alias[IngredientUnitModel.normalize(unit.abbreviation)] = unit
                if unit.plural_abbreviation:
                    units_by_alias[IngredientUnitModel.normalize(unit.plural_abbreviation)] = unit

                for alias in unit.aliases or []:
                    if alias.name:
                        units_by_alias[IngredientUnitModel.normalize(alias.name)] = unit

            self._units_by_alias = units_by_alias

        return self._units_by_alias

    @property
    def food_fuzzy_match_threshold(self) -> int:
        """Minimum threshold to fuzzy match against a database food search"""

        return 85

    @property
    def unit_fuzzy_match_threshold(self) -> int:
        """Minimum threshold to fuzzy match against a database unit search"""

        return 70

    @abstractmethod
    def parse_one(self, ingredient_string: str) -> ParsedIngredient: ...

    @abstractmethod
    def parse(self, ingredients: list[str]) -> list[ParsedIngredient]: ...

    @classmethod
    def find_match(cls, match_value: str, *, store_map: dict[str, T], fuzzy_match_threshold: int = 0) -> T | None:
        # check for literal matches
        if match_value in store_map:
            return store_map[match_value]

        # fuzzy match against food store
        fuzz_result = process.extractOne(
            match_value, store_map.keys(), scorer=fuzz.ratio, score_cutoff=fuzzy_match_threshold
        )
        if fuzz_result is None:
            return None

        return store_map[fuzz_result[0]]

    def find_food_match(self, food: IngredientFood | CreateIngredientFood | str) -> IngredientFood | None:
        if isinstance(food, IngredientFood):
            return food

        food_name = food if isinstance(food, str) else food.name
        match_value = IngredientFoodModel.normalize(food_name)
        return self.find_match(
            match_value,
            store_map=self.foods_by_alias,
            fuzzy_match_threshold=self.food_fuzzy_match_threshold,
        )

    def find_unit_match(self, unit: IngredientUnit | CreateIngredientUnit | str) -> IngredientUnit | None:
        if isinstance(unit, IngredientUnit):
            return unit

        unit_name = unit if isinstance(unit, str) else unit.name
        match_value = IngredientUnitModel.normalize(unit_name)
        return self.find_match(
            match_value,
            store_map=self.units_by_alias,
            fuzzy_match_threshold=self.unit_fuzzy_match_threshold,
        )

    def find_ingredient_match(self, ingredient: ParsedIngredient) -> ParsedIngredient:
        if ingredient.ingredient.food and (food_match := self.find_food_match(ingredient.ingredient.food)):
            ingredient.ingredient.food = food_match

        if ingredient.ingredient.unit and (unit_match := self.find_unit_match(ingredient.ingredient.unit)):
            ingredient.ingredient.unit = unit_match

        # Parser might have wrongly split a food into a unit and food.
        if isinstance(ingredient.ingredient.food, CreateIngredientFood) and isinstance(
            ingredient.ingredient.unit, CreateIngredientUnit
        ):
            if food_match := self.find_food_match(
                f"{ingredient.ingredient.unit.name} {ingredient.ingredient.food.name}"
            ):
                ingredient.ingredient.food = food_match
                ingredient.ingredient.unit = None

        return ingredient


class BruteForceParser(ABCIngredientParser):
    """
    Brute force ingredient parser.
    """

    def parse_one(self, ingredient: str) -> ParsedIngredient:
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
