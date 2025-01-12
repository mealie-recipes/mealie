import json
import pathlib
from collections.abc import Generator
from functools import cached_property

from mealie.schema.labels import MultiPurposeLabelOut, MultiPurposeLabelSave
from mealie.schema.recipe.recipe_ingredient import (
    IngredientFood,
    IngredientUnit,
    SaveIngredientFood,
    SaveIngredientUnit,
)
from mealie.services.group_services.labels_service import MultiPurposeLabelService

from ._abstract_seeder import AbstractSeeder
from .resources import foods, units


class MultiPurposeLabelSeeder(AbstractSeeder):
    @cached_property
    def service(self):
        return MultiPurposeLabelService(self.repos)

    def get_file(self, locale: str | None = None) -> pathlib.Path:
        # Get the labels from the foods seed file now
        locale_path = self.resources / "foods" / "locales" / f"{locale}.json"
        return locale_path if locale_path.exists() else foods.en_US

    def get_all_labels(self) -> list[MultiPurposeLabelOut]:
        return self.repos.group_multi_purpose_labels.get_all()

    def load_data(self, locale: str | None = None) -> Generator[MultiPurposeLabelSave, None, None]:
        file = self.get_file(locale)

        current_label_names = {label.name for label in self.get_all_labels()}
        # load from the foods locale file and remove any empty strings
        seed_label_names = set(filter(None, json.loads(file.read_text(encoding="utf-8")).keys()))  # type: set[str]
        # only seed new labels
        to_seed_labels = seed_label_names - current_label_names
        for label in to_seed_labels:
            yield MultiPurposeLabelSave(
                name=label,
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

    def get_all_units(self) -> list[IngredientUnit]:
        return self.repos.ingredient_units.get_all()

    def load_data(self, locale: str | None = None) -> Generator[SaveIngredientUnit, None, None]:
        file = self.get_file(locale)

        seen_unit_names = {unit.name for unit in self.get_all_units()}
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

    def get_label(self, value: str) -> MultiPurposeLabelOut | None:
        return self.repos.group_multi_purpose_labels.get_one(value, "name")

    def get_all_foods(self) -> list[IngredientFood]:
        return self.repos.ingredient_foods.get_all()

    def load_data(self, locale: str | None = None) -> Generator[SaveIngredientFood, None, None]:
        file = self.get_file(locale)

        # get all current unique foods
        seen_foods_names = {food.name for food in self.get_all_foods()}
        for label, values in json.loads(file.read_text(encoding="utf-8")).items():
            label_out = self.get_label(label)

            for food_name, attributes in values["foods"].items():
                if food_name in seen_foods_names:
                    continue

                seen_foods_names.add(food_name)
                yield SaveIngredientFood(
                    group_id=self.repos.group_id,
                    name=attributes["name"],
                    plural_name=attributes.get("plural_name"),
                    description="",  # description expected to be empty string by UnitFoodBase class
                    label_id=label_out.id if label_out and label_out.id else None,
                )

    def seed(self, locale: str | None = None) -> None:
        self.logger.info("Seeding Ingredient Foods")
        for food in self.load_data(locale):
            try:
                self.repos.ingredient_foods.create(food)
            except Exception as e:
                self.logger.error(e)
