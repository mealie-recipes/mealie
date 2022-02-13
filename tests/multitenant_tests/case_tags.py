from typing import Tuple

from requests import Response

from mealie.schema.recipe.recipe import RecipeTag
from mealie.schema.recipe.recipe_category import TagSave
from tests import utils
from tests.multitenant_tests.case_abc import ABCMultiTenantTestCase
from tests.utils import routes


class TagsTestCase(ABCMultiTenantTestCase):
    items: list[RecipeTag]

    def seed_action(self, group_id: str) -> set[int]:
        tag_ids: set[int] = set()
        for _ in range(10):
            tag = self.database.tags.create(
                TagSave(
                    group_id=group_id,
                    name=utils.random_string(10),
                )
            )

            tag_ids.add(tag.id)
            self.items.append(tag)

        return tag_ids

    def seed_multi(self, group1_id: str, group2_id: str) -> Tuple[set[str], set[str]]:
        g1_item_ids = set()
        g2_item_ids = set()

        for group_id, item_ids in [(group1_id, g1_item_ids), (group2_id, g2_item_ids)]:
            for _ in range(10):
                name = utils.random_string(10)
                category = self.database.tags.create(
                    TagSave(
                        group_id=group_id,
                        name=name,
                    )
                )
                item_ids.add(category.id)
                self.items.append(category)

        return g1_item_ids, g2_item_ids

    def get_all(self, token: str) -> Response:
        return self.client.get(routes.RoutesTags.base, headers=token)

    def cleanup(self) -> None:
        for item in self.items:
            self.database.tags.delete(item.id)
