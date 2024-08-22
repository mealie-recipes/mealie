from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import UUID4, BaseModel
from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session

from mealie.db.models.recipe.ingredient import IngredientFoodModel, IngredientUnitModel
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    CreateIngredientUnit,
    IngredientFood,
    IngredientUnit,
    ParsedIngredient,
)
from mealie.schema.response.pagination import PaginationQuery

T = TypeVar("T", bound=BaseModel)


class DataMatcher:
    def __init__(
        self,
        repos: AllRepositories,
        food_fuzzy_match_threshold: int = 85,
        unit_fuzzy_match_threshold: int = 70,
    ) -> None:
        self.repos = repos

        self._food_fuzzy_match_threshold = food_fuzzy_match_threshold
        self._unit_fuzzy_match_threshold = unit_fuzzy_match_threshold
        self._foods_by_alias: dict[str, IngredientFood] | None = None
        self._units_by_alias: dict[str, IngredientUnit] | None = None

    @property
    def foods_by_alias(self) -> dict[str, IngredientFood]:
        if self._foods_by_alias is None:
            foods_repo = self.repos.ingredient_foods
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
            units_repo = self.repos.ingredient_units
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
            fuzzy_match_threshold=self._food_fuzzy_match_threshold,
        )

    def find_unit_match(self, unit: IngredientUnit | CreateIngredientUnit | str) -> IngredientUnit | None:
        if isinstance(unit, IngredientUnit):
            return unit

        unit_name = unit if isinstance(unit, str) else unit.name
        match_value = IngredientUnitModel.normalize(unit_name)
        return self.find_match(
            match_value,
            store_map=self.units_by_alias,
            fuzzy_match_threshold=self._unit_fuzzy_match_threshold,
        )


class ABCIngredientParser(ABC):
    """
    Abstract class for ingredient parsers.
    """

    def __init__(self, group_id: UUID4, session: Session) -> None:
        self.group_id = group_id
        self.session = session
        self.data_matcher = DataMatcher(self._repos, self.food_fuzzy_match_threshold, self.unit_fuzzy_match_threshold)

    @property
    def _repos(self) -> AllRepositories:
        return get_repositories(self.session, group_id=self.group_id)

    @property
    def food_fuzzy_match_threshold(self) -> int:
        """Minimum threshold to fuzzy match against a database food search"""

        return 85

    @property
    def unit_fuzzy_match_threshold(self) -> int:
        """Minimum threshold to fuzzy match against a database unit search"""

        return 70

    @abstractmethod
    async def parse_one(self, ingredient_string: str) -> ParsedIngredient: ...

    @abstractmethod
    async def parse(self, ingredients: list[str]) -> list[ParsedIngredient]: ...

    def find_ingredient_match(self, ingredient: ParsedIngredient) -> ParsedIngredient:
        if ingredient.ingredient.food and (food_match := self.data_matcher.find_food_match(ingredient.ingredient.food)):
            ingredient.ingredient.food = food_match

        if ingredient.ingredient.unit and (unit_match := self.data_matcher.find_unit_match(ingredient.ingredient.unit)):
            ingredient.ingredient.unit = unit_match

        # Parser might have wrongly split a food into a unit and food.
        if isinstance(ingredient.ingredient.food, CreateIngredientFood) and isinstance(
            ingredient.ingredient.unit, CreateIngredientUnit
        ):
            if food_match := self.data_matcher.find_food_match(
                f"{ingredient.ingredient.unit.name} {ingredient.ingredient.food.name}"
            ):
                ingredient.ingredient.food = food_match
                ingredient.ingredient.unit = None

        return ingredient
