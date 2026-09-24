import pathlib
from collections.abc import Generator
from functools import cached_property

from mealie.lang.locale_config import resolve_food_plural, resolve_plural
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


class IngredientUnitsSeeder(AbstractSeeder):
    @classmethod
    def get_file(cls, locale: str | None = None) -> pathlib.Path:
        locale_path = cls.resources / "units" / "locales" / f"{locale}.json"
        return locale_path if locale_path.exists() else units.en_US

    def get_all_units(self) -> list[IngredientUnit]:
        return self.repos.ingredient_units.get_all()

    def load_data(self, locale: str | None = None) -> Generator[SaveIngredientUnit]:
        file = self.get_file(locale)

        seen_unit_names = {unit.name for unit in self.get_all_units()}
        for key, unit in self.load_file(file).items():
            if unit["name"] in seen_unit_names:
                continue

            seen_unit_names.add(unit["name"])

            # an unrecognized key has nothing to compare against, so treat it as untranslated
            source = self.source_data.get(key, unit)
            yield SaveIngredientUnit(
                group_id=self.repos.group_id,
                name=unit["name"],
                plural_name=resolve_plural(
                    source_singular=source["name"],
                    source_plural=source.get("plural_name"),
                    singular=unit["name"],
                    plural=unit.get("plural_name"),
                ),
                description=unit["description"],
                abbreviation=unit["abbreviation"],
                plural_abbreviation=resolve_plural(
                    source_singular=source["abbreviation"],
                    source_plural=source.get("plural_abbreviation"),
                    singular=unit["abbreviation"],
                    plural=unit.get("plural_abbreviation"),
                ),
            )

    def seed(self, locale: str | None = None) -> None:
        self.logger.info("Seeding Ingredient Units")
        for unit in self.load_data(locale):
            try:
                self.repos.ingredient_units.create(unit)
            except Exception as e:
                self.logger.error(e)


class IngredientFoodsSeeder(AbstractSeeder):
    """Seeds both the foods and the labels that group them, from a single locale file."""

    @cached_property
    def label_service(self) -> MultiPurposeLabelService:
        return MultiPurposeLabelService(self.repos)

    @classmethod
    def get_file(cls, locale: str | None = None) -> pathlib.Path:
        locale_path = cls.resources / "foods" / "locales" / f"{locale}.json"
        return locale_path if locale_path.exists() else foods.en_US

    def get_label(self, value: str) -> MultiPurposeLabelOut | None:
        return self.repos.group_multi_purpose_labels.get_one(value, "name")

    def get_all_foods(self) -> list[IngredientFood]:
        return self.repos.ingredient_foods.get_all()

    def seed_labels(self, locale: str | None = None) -> None:
        """Create any labels from the seed file that don't already exist in the group."""
        seen_label_names = {label.name for label in self.repos.group_multi_purpose_labels.get_all()}
        for label in self.load_file(self.get_file(locale)).values():
            name = label["name"]
            if not name or name in seen_label_names:
                continue

            seen_label_names.add(name)
            try:
                self.label_service.create_one(MultiPurposeLabelSave(name=name, group_id=self.repos.group_id))
            except Exception as e:
                self.logger.error(e)

    def load_data(self, locale: str | None = None) -> Generator[SaveIngredientFood]:
        file = self.get_file(locale)

        # de-duplicate on the localized name rather than the English seed key, otherwise seeding
        # a second locale skips every food whose English key already exists in the group
        seen_foods_names = {food.name for food in self.get_all_foods()}
        for label_key, values in self.load_file(file).items():
            label_out = self.get_label(values["name"])
            source_foods = self.source_data.get(label_key, {}).get("foods", {})

            for food_key, attributes in values["foods"].items():
                name = attributes["name"]
                if name in seen_foods_names:
                    continue

                seen_foods_names.add(name)

                # an unrecognized key has nothing to compare against, so treat it as untranslated
                source = source_foods.get(food_key, attributes)
                yield SaveIngredientFood(
                    group_id=self.repos.group_id,
                    name=name,
                    plural_name=resolve_food_plural(
                        source_singular=source["name"],
                        source_plural=source.get("plural_name"),
                        singular=name,
                        plural=attributes.get("plural_name"),
                        locale=locale,
                    ),
                    description="",  # description expected to be empty string by UnitFoodBase class
                    label_id=label_out.id if label_out and label_out.id else None,
                )

    def seed(self, locale: str | None = None) -> None:
        self.logger.info("Seeding Ingredient Foods")
        # labels must exist before foods so each food can be linked to its label
        self.seed_labels(locale)

        to_seed = list(self.load_data(locale))
        if not to_seed:
            return

        try:
            self.repos.ingredient_foods.create_many(to_seed)
        except Exception:
            self.logger.exception("Failed to seed ingredient foods in bulk, falling back to one at a time")
            for food in to_seed:
                try:
                    self.repos.ingredient_foods.create(food)
                except Exception as e:
                    self.logger.error(e)
