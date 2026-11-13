from pydantic import ConfigDict
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.recipe import Tool

from .recipe_organizers import ToolOut


class ToolWithRecipes(ToolOut):
    recipes: list[RecipeSummary] = []
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(Tool.households_with_tool),
            selectinload(Tool.recipes).options(*RecipeSummary.loader_options()),
        ]


from .recipe import RecipeSummary  # noqa: E402

ToolWithRecipes.model_rebuild()
