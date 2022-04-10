import json
from collections.abc import Generator

from mealie.schema.labels import MultiPurposeLabelSave
from mealie.schema.recipe.recipe_ingredient import SaveIngredientFood, SaveIngredientUnit

from ._abstract_seeder import AbstractSeeder
from .resources import foods, labels, units


class MultiPurposeLabelSeeder(AbstractSeeder):
    def load_data(self) -> Generator[MultiPurposeLabelSave, None, None]:
        file = labels.en_US

        for label in json.loads(file.read_text()):
            yield MultiPurposeLabelSave(
                name=label["name"],
                group_id=self.group_id,
            )

    def seed(self) -> None:
        self.logger.info("Seeding MultiPurposeLabel")
        for label in self.load_data():
            try:
                self.repos.group_multi_purpose_labels.create(label)
            except Exception as e:
                self.logger.error(e)


class IngredientUnitsSeeder(AbstractSeeder):
    def load_data(self) -> Generator[SaveIngredientUnit, None, None]:
        file = units.en_US
        for unit in json.loads(file.read_text()).values():
            yield SaveIngredientUnit(
                group_id=self.group_id,
                name=unit["name"],
                description=unit["description"],
                abbreviation=unit["abbreviation"],
            )

    def seed(self) -> None:
        self.logger.info("Seeding Ingredient Units")
        for unit in self.load_data():
            try:
                self.repos.ingredient_units.create(unit)
            except Exception as e:
                self.logger.error(e)


class IngredientFoodsSeeder(AbstractSeeder):
    def load_data(self) -> Generator[SaveIngredientFood, None, None]:
        file = foods.en_US
        seed_foods: dict[str, str] = json.loads(file.read_text())
        for food in seed_foods.values():
            yield SaveIngredientFood(
                group_id=self.group_id,
                name=food,
                description="",
            )

    def seed(self) -> None:
        self.logger.info("Seeding Ingredient Foods")
        for food in self.load_data():
            try:
                self.repos.ingredient_foods.create(food)
            except Exception as e:
                self.logger.error(e)
