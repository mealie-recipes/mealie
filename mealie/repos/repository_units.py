from collections.abc import Iterable

from pydantic import UUID4, BaseModel
from sqlalchemy import select

from mealie.db.models.recipe.ingredient import IngredientUnitModel
from mealie.lang.providers import get_locale_context
from mealie.schema.recipe.recipe_ingredient import IngredientUnit, StandardizedUnitType

from .repository_generic import GroupRepositoryGeneric


class RepositoryUnit(GroupRepositoryGeneric[IngredientUnit, IngredientUnitModel]):
    _standardized_unit_map: dict[str, str] | None = None

    @property
    def standardized_unit_map(self) -> dict[str, str]:
        """A map of potential known units to its standardized name in our seed data"""

        if self._standardized_unit_map is None:
            from .seed.seeders import IngredientUnitsSeeder

            ctx = get_locale_context()
            if ctx:
                locale = ctx[1].key
            else:
                locale = None

            self._standardized_unit_map = {}
            locale_file = IngredientUnitsSeeder.get_file(locale=locale)
            for unit_key, unit in IngredientUnitsSeeder.load_file(locale_file).items():
                for prop in ["name", "plural_name", "abbreviation"]:
                    val = unit.get(prop)
                    if val and isinstance(val, str):
                        self._standardized_unit_map[val.strip().lower()] = unit_key

        return self._standardized_unit_map

    def _get_unit(self, id: UUID4) -> IngredientUnitModel:
        stmt = select(self.model).filter_by(**self._filter_builder(**{"id": id}))
        return self.session.execute(stmt).scalars().one()

    def _add_standardized_unit(self, data: BaseModel | dict) -> dict:
        if not isinstance(data, dict):
            data = data.model_dump()

        # Don't overwrite user data if it exists
        if data.get("standard_quantity") is not None or data.get("standard_unit") is not None:
            return data

        # Compare name attrs to translation files and see if there's a match to a known standard unit
        for prop in ["name", "plural_name", "abbreviation", "plural_abbreviation"]:
            val = data.get(prop)
            if not (val and isinstance(val, str)):
                continue

            standardized_unit_key = self.standardized_unit_map.get(val.strip().lower())
            if not standardized_unit_key:
                continue

            match standardized_unit_key:
                case "teaspoon":
                    data["standard_quantity"] = 1 / 6
                    data["standard_unit"] = StandardizedUnitType.FLUID_OUNCE
                case "tablespoon":
                    data["standard_quantity"] = 1 / 2
                    data["standard_unit"] = StandardizedUnitType.FLUID_OUNCE
                case "cup":
                    data["standard_quantity"] = 1
                    data["standard_unit"] = StandardizedUnitType.CUP
                case "fluid-ounce":
                    data["standard_quantity"] = 1
                    data["standard_unit"] = StandardizedUnitType.FLUID_OUNCE
                case "pint":
                    data["standard_quantity"] = 2
                    data["standard_unit"] = StandardizedUnitType.CUP
                case "quart":
                    data["standard_quantity"] = 4
                    data["standard_unit"] = StandardizedUnitType.CUP
                case "gallon":
                    data["standard_quantity"] = 16
                    data["standard_unit"] = StandardizedUnitType.CUP
                case "milliliter":
                    data["standard_quantity"] = 1
                    data["standard_unit"] = StandardizedUnitType.MILLILITER
                case "liter":
                    data["standard_quantity"] = 1
                    data["standard_unit"] = StandardizedUnitType.LITER
                case "pound":
                    data["standard_quantity"] = 1
                    data["standard_unit"] = StandardizedUnitType.POUND
                case "ounce":
                    data["standard_quantity"] = 1
                    data["standard_unit"] = StandardizedUnitType.OUNCE
                case "gram":
                    data["standard_quantity"] = 1
                    data["standard_unit"] = StandardizedUnitType.GRAM
                case "kilogram":
                    data["standard_quantity"] = 1
                    data["standard_unit"] = StandardizedUnitType.KILOGRAM
                case "milligram":
                    data["standard_quantity"] = 1 / 1000
                    data["standard_unit"] = StandardizedUnitType.GRAM
                case _:
                    continue

        return data

    def create(self, data: IngredientUnit | dict) -> IngredientUnit:
        data = self._add_standardized_unit(data)
        return super().create(data)

    def create_many(self, data: Iterable[IngredientUnit | dict]) -> list[IngredientUnit]:
        data = [self._add_standardized_unit(i) for i in data]
        return super().create_many(data)

    def merge(self, from_unit: UUID4, to_unit: UUID4) -> IngredientUnit | None:
        from_model = self._get_unit(from_unit)
        to_model = self._get_unit(to_unit)

        to_model.ingredients += from_model.ingredients

        try:
            self.session.delete(from_model)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return self.get_one(to_unit)
