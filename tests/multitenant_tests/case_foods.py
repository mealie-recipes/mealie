from typing import Tuple

from requests import Response

from mealie.schema.recipe.recipe_ingredient import IngredientFood, SaveIngredientFood
from tests import utils
from tests.multitenant_tests.case_abc import ABCMultiTenantTestCase
from tests.utils import routes


class FoodsTestCase(ABCMultiTenantTestCase):
    items: list[IngredientFood]

    def seed_action(self, group_id: str) -> set[int]:
        food_ids: set[int] = set()
        for _ in range(10):
            food = self.database.ingredient_foods.create(
                SaveIngredientFood(
                    group_id=group_id,
                    name=utils.random_string(10),
                )
            )

            food_ids.add(food.id)
            self.items.append(food)

        return food_ids

    def seed_multi(self, group1_id: str, group2_id: str) -> Tuple[set[str], set[str]]:
        g1_item_ids = set()
        g2_item_ids = set()

        for group_id, item_ids in [(group1_id, g1_item_ids), (group2_id, g2_item_ids)]:
            for _ in range(10):
                name = utils.random_string(10)
                food = self.database.ingredient_foods.create(
                    SaveIngredientFood(
                        group_id=group_id,
                        name=name,
                    )
                )
                item_ids.add(food.id)
                self.items.append(food)

        return g1_item_ids, g2_item_ids

    def get_all(self, token: str) -> Response:
        return self.client.get(routes.RoutesFoods.base, headers=token)

    def cleanup(self) -> None:
        for item in self.items:
            self.database.ingredient_foods.delete(item.id)
