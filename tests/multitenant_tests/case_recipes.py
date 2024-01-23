from requests import Response

from mealie.schema.recipe.recipe import Recipe
from tests import utils
from tests.multitenant_tests.case_abc import ABCMultiTenantTestCase
from tests.utils import api_routes


class RecipesTestCase(ABCMultiTenantTestCase):
    items: list[Recipe]

    def seed_action(self, group_id: str) -> set[str]:
        ids: set[str] = set()
        for _ in range(10):
            recipe = self.database.recipes.create(
                Recipe(
                    group_id=group_id,
                    name=utils.random_string(10),
                )
            )

            ids.add(str(recipe.id))
            self.items.append(recipe)

        return ids

    def seed_multi(self, group1_id: str, group2_id: str) -> tuple[set[str], set[str]]:
        g1_ids: set[str] = set()
        g2_ids: set[str] = set()

        for _ in range(10):
            name = utils.random_string(10)
            for group_id, ids in [(group1_id, g1_ids), (group2_id, g2_ids)]:
                recipe = self.database.recipes.create(
                    Recipe(
                        group_id=group_id,
                        name=name,
                    )
                )
                ids.add(str(recipe.id))
                self.items.append(recipe)

        return g1_ids, g2_ids

    def get_all(self, token: str) -> Response:
        return self.client.get(api_routes.recipes, headers=token)

    def cleanup(self) -> None:
        for item in self.items:
            self.database.recipes.delete(item.id, "id")
