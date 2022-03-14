import json
from collections.abc import Generator

from mealie.schema.labels import MultiPurposeLabelSave
from mealie.schema.recipe.recipe_ingredient import SaveIngredientFood, SaveIngredientUnit

from ._abstract_seeder import AbstractSeeder


class MultiPurposeLabelSeeder(AbstractSeeder):
    def load_data(self) -> Generator[MultiPurposeLabelSave, None, None]:
        file = self.resources / "labels" / "en-us.json"

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
        file = self.resources / "units" / "en-us.json"
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
        file = self.resources / "foods" / "en-us.json"
        foods: dict[str, str] = json.loads(file.read_text())
        for food in foods.values():
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
