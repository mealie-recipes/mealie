from requests import Response

from mealie.schema.recipe.recipe_tool import RecipeToolSave
from tests import utils
from tests.multitenant_tests.case_abc import ABCMultiTenantTestCase
from tests.utils import routes


class ToolsTestCase(ABCMultiTenantTestCase):
    def seed_action(self, group_id: str) -> set[int]:
        tool_ids: set[int] = set()
        for _ in range(10):
            tool = self.database.tools.create(
                RecipeToolSave(
                    group_id=group_id,
                    name=utils.random_string(10),
                )
            )

            tool_ids.add(tool.id)

        return tool_ids

    def get_all(self, token: str) -> Response:
        return self.client.get(routes.RoutesTools.base, headers=token)
