from typing import Tuple

from requests import Response

from mealie.schema.recipe.recipe_ingredient import IngredientUnit, SaveIngredientUnit
from tests import utils
from tests.multitenant_tests.case_abc import ABCMultiTenantTestCase
from tests.utils import routes


class UnitsTestCase(ABCMultiTenantTestCase):
    items: list[IngredientUnit]

    def seed_action(self, group_id: str) -> set[int]:
        unit_ids: set[int] = set()
        for _ in range(10):
            unit = self.database.ingredient_units.create(
                SaveIngredientUnit(
                    group_id=group_id,
                    name=utils.random_string(10),
                )
            )

            unit_ids.add(str(unit.id))
            self.items.append(unit)

        return unit_ids

    def seed_multi(self, group1_id: str, group2_id: str) -> Tuple[set[str], set[str]]:
        g1_item_ids = set()
        g2_item_ids = set()

        for group_id, item_ids in [(group1_id, g1_item_ids), (group2_id, g2_item_ids)]:
            for _ in range(10):
                name = utils.random_string(10)
                food = self.database.ingredient_units.create(
                    SaveIngredientUnit(
                        group_id=group_id,
                        name=name,
                    )
                )
                item_ids.add(str(food.id))
                self.items.append(food)

        return g1_item_ids, g2_item_ids

    def get_all(self, token: str) -> Response:
        return self.client.get(routes.RoutesUnits.base, headers=token)

    def cleanup(self) -> None:
        for item in self.items:
            self.database.ingredient_units.delete(item.id)
