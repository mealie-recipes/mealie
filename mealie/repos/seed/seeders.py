import json
import pathlib
from collections.abc import Generator
from functools import cached_property

from mealie.schema.labels import MultiPurposeLabelSave
from mealie.schema.recipe.recipe_ingredient import SaveIngredientFood, SaveIngredientUnit
from mealie.services.group_services.labels_service import MultiPurposeLabelService

from ._abstract_seeder import AbstractSeeder
from .resources import foods, labels, units


class MultiPurposeLabelSeeder(AbstractSeeder):
    @cached_property
    def service(self):
        return MultiPurposeLabelService(self.repos)

    def get_file(self, locale: str | None = None) -> pathlib.Path:
        locale_path = self.resources / "labels" / "locales" / f"{locale}.json"
        return locale_path if locale_path.exists() else labels.en_US

    def load_data(self, locale: str | None = None) -> Generator[MultiPurposeLabelSave, None, None]:
        file = self.get_file(locale)

        seen_label_names = set()
        for label in json.loads(file.read_text(encoding="utf-8")):
            if label["name"] in seen_label_names:
                continue

            seen_label_names.add(label["name"])
            yield MultiPurposeLabelSave(
                name=label["name"],
                group_id=self.repos.group_id,
            )

    def seed(self, locale: str | None = None) -> None:
        self.logger.info("Seeding MultiPurposeLabel")
        for label in self.load_data(locale):
            try:
                self.service.create_one(label)
            except Exception as e:
                self.logger.error(e)


class IngredientUnitsSeeder(AbstractSeeder):
    def get_file(self, locale: str | None = None) -> pathlib.Path:
        locale_path = self.resources / "units" / "locales" / f"{locale}.json"
        return locale_path if locale_path.exists() else units.en_US

    def load_data(self, locale: str | None = None) -> Generator[SaveIngredientUnit, None, None]:
        file = self.get_file(locale)

        seen_unit_names = set()
        for unit in json.loads(file.read_text(encoding="utf-8")).values():
            if unit["name"] in seen_unit_names:
                continue

            seen_unit_names.add(unit["name"])
            yield SaveIngredientUnit(
                group_id=self.repos.group_id,
                name=unit["name"],
                plural_name=unit.get("plural_name"),
                description=unit["description"],
                abbreviation=unit["abbreviation"],
                plural_abbreviation=unit.get("plural_abbreviation"),
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

        seed_foods_names = set()
        for food in json.loads(file.read_text(encoding="utf-8")).values():
            if food["name"] in seed_foods_names:
                continue

            seed_foods_names.add(food["name"])
            yield SaveIngredientFood(
                group_id=self.repos.group_id,
                name=food["name"],
                plural_name=food.get("plural_name"),
                description="",
            )

    def seed(self, locale: str | None = None) -> None:
        self.logger.info("Seeding Ingredient Foods")
        for food in self.load_data(locale):
            try:
                self.repos.ingredient_foods.create(food)
            except Exception as e:
                self.logger.error(e)
