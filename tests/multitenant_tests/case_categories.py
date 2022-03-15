from requests import Response

from mealie.schema.recipe.recipe import RecipeCategory
from mealie.schema.recipe.recipe_category import CategorySave
from tests import utils
from tests.multitenant_tests.case_abc import ABCMultiTenantTestCase
from tests.utils import routes


class CategoryTestCase(ABCMultiTenantTestCase):
    items: list[RecipeCategory]

    def seed_action(self, group_id: str) -> set[int]:
        category_ids: set[int] = set()
        for _ in range(10):
            category = self.database.categories.create(
                CategorySave(
                    group_id=group_id,
                    name=utils.random_string(10),
                )
            )

            self.items.append(category)
            category_ids.add(str(category.id))

        return category_ids

    def seed_multi(self, group1_id: str, group2_id: str) -> tuple[set[str], set[str]]:
        g1_item_ids = set()
        g2_item_ids = set()

        for group_id, item_ids in [(group1_id, g1_item_ids), (group2_id, g2_item_ids)]:
            for _ in range(10):
                name = utils.random_string(10)
                category = self.database.categories.create(
                    CategorySave(
                        group_id=group_id,
                        name=name,
                    )
                )
                item_ids.add(str(category.id))
                self.items.append(category)

        return g1_item_ids, g2_item_ids

    def get_all(self, token: str) -> Response:
        return self.client.get(routes.RoutesCategory.base, headers=token)

    def cleanup(self) -> None:
        for item in self.items:
            self.database.categories.delete(item.id)
