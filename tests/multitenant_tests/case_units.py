from requests import Response

from mealie.schema.recipe.recipe_ingredient import SaveIngredientUnit
from tests import utils
from tests.multitenant_tests.case_abc import ABCMultiTenanatTestCase
from tests.utils import routes


class UnitsTestCase(ABCMultiTenanatTestCase):
    def seed_action(self, group_id: str) -> set[int]:
        unit_ids: set[int] = set()
        for _ in range(10):
            food = self.database.ingredient_units.create(
                SaveIngredientUnit(
                    group_id=group_id,
                    name=utils.random_string(10),
                )
            )

            unit_ids.add(food.id)

        return unit_ids

    def get_all(self, token: str) -> Response:
        return self.client.get(routes.RoutesUnits.base, headers=token)
