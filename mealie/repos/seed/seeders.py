import json
import pathlib
from collections.abc import Generator

from mealie.schema.labels import MultiPurposeLabelSave
from mealie.schema.recipe.recipe_ingredient import SaveIngredientFood, SaveIngredientUnit

from ._abstract_seeder import AbstractSeeder
from .resources import foods, labels, units


class MultiPurposeLabelSeeder(AbstractSeeder):
    def get_file(self, locale: str | None = None) -> pathlib.Path:
        locale_path = self.resources / "labels" / "locales" / f"{locale}.json"
        return locale_path if locale_path.exists() else labels.en_US

    def load_data(self, locale: str | None = None) -> Generator[MultiPurposeLabelSave, None, None]:
        file = self.get_file(locale)

        for label in json.loads(file.read_text()):
            yield MultiPurposeLabelSave(
                name=label["name"],
                group_id=self.group_id,
            )

    def seed(self, locale: str | None = None) -> None:
        self.logger.info("Seeding MultiPurposeLabel")
        for label in self.load_data(locale):
            try:
                self.repos.group_multi_purpose_labels.create(label)
            except Exception as e:
                self.logger.error(e)


class IngredientUnitsSeeder(AbstractSeeder):
    def get_file(self, locale: str | None = None) -> pathlib.Path:
        locale_path = self.resources / "units" / "locales" / f"{locale}.json"
        return locale_path if locale_path.exists() else units.en_US

    def load_data(self, locale: str | None = None) -> Generator[SaveIngredientUnit, None, None]:
        file = self.get_file(locale)

        for unit in json.loads(file.read_text()).values():
            yield SaveIngredientUnit(
                group_id=self.group_id,
                name=unit["name"],
                description=unit["description"],
                abbreviation=unit["abbreviation"],
            )

    def seed(self, locale: str | None = None) -> None:
        self.logger.info("Seeding Ingredient Units")
        for unit in self.load_data(locale):
            try:
                self.repos.ingredient_units.create(unit)
            except Exception as e:
                self.logger.error(e)


class IngredientFoodsSeeder(AbstractSeeder):
    def get_file(self, locale: str | None = None) -> pathlib.Path:
        locale_path = self.resources / "foods" / "locales" / f"{locale}.json"
        return locale_path if locale_path.exists() else foods.en_US

    def load_data(self, locale: str | None = None) -> Generator[SaveIngredientFood, None, None]:
        file = self.get_file(locale)

        seed_foods: dict[str, str] = json.loads(file.read_text())
        for food in seed_foods.values():
            yield SaveIngredientFood(
                group_id=self.group_id,
                name=food,
                description="",
            )

    def seed(self, locale: str | None = None) -> None:
        self.logger.info("Seeding Ingredient Foods")
        for food in self.load_data(locale):
            try:
                self.repos.ingredient_foods.create(food)
            except Exception as e:
                self.logger.error(e)
