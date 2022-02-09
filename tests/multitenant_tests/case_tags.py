from requests import Response

from mealie.schema.recipe.recipe_category import TagSave
from tests import utils
from tests.multitenant_tests.case_abc import ABCMultiTenanatTestCase
from tests.utils import routes


class TagsTestCase(ABCMultiTenanatTestCase):
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

        return tag_ids

    def get_all(self, token: str) -> Response:
        return self.client.get(routes.RoutesTags.base, headers=token)
