from requests import Response

from mealie.schema.recipe.recipe import RecipeTool
from mealie.schema.recipe.recipe_tool import RecipeToolSave
from tests import utils
from tests.multitenant_tests.case_abc import ABCMultiTenantTestCase
from tests.utils import api_routes


class ToolsTestCase(ABCMultiTenantTestCase):
    items: list[RecipeTool]

    def seed_action(self, group_id: str) -> set[str]:
        tool_ids: set[str] = set()
        for _ in range(10):
            tool = self.database.tools.create(
                RecipeToolSave(
                    group_id=group_id,
                    name=utils.random_string(10),
                )
            )

            tool_ids.add(str(tool.id))
            self.items.append(tool)

        return tool_ids

    def seed_multi(self, group1_id: str, group2_id: str) -> tuple[set[str], set[str]]:
        g1_item_ids: set[str] = set()
        g2_item_ids: set[str] = set()

        for _ in range(10):
            name = utils.random_string(10)
            for group_id, item_ids in [(group1_id, g1_item_ids), (group2_id, g2_item_ids)]:
                tool = self.database.tools.create(
                    RecipeToolSave(
                        group_id=group_id,
                        name=name,
                    )
                )
                item_ids.add(str(tool.id))
                self.items.append(tool)

        return g1_item_ids, g2_item_ids

    def get_all(self, token: str) -> Response:
        return self.client.get(api_routes.organizers_tools, headers=token)

    def cleanup(self) -> None:
        for item in self.items:
            self.database.tools.delete(item.id)
