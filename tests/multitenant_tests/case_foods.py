from requests import Response

from mealie.schema.recipe.recipe_ingredient import SaveIngredientFood
from tests import utils
from tests.multitenant_tests.case_abc import ABCMultiTenanatTestCase
from tests.utils import routes


class FoodsTestCase(ABCMultiTenanatTestCase):
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

        return food_ids

    def get_all(self, token: str) -> Response:
        return self.client.get(routes.RoutesFoods.base, headers=token)
