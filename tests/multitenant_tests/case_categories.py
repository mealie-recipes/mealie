from requests import Response

from mealie.schema.recipe.recipe_category import CategorySave
from tests import utils
from tests.multitenant_tests.case_abc import ABCMultiTenantTestCase
from tests.utils import routes


class CategoryTestCase(ABCMultiTenantTestCase):
    def seed_action(self, group_id: str) -> set[int]:
        category_ids: set[int] = set()
        for _ in range(10):
            category = self.database.categories.create(
                CategorySave(
                    group_id=group_id,
                    name=utils.random_string(10),
                )
            )

            category_ids.add(category.id)

        return category_ids

    def get_all(self, token: str) -> Response:
        return self.client.get(routes.RoutesCategory.base, headers=token)
