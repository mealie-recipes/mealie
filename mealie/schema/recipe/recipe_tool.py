from pydantic import ConfigDict
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.recipe import RecipeModel, Tool

from .recipe_organizers import ToolOut


class ToolWithRecipes(ToolOut):
    recipes: list[RecipeSummary] = []
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(Tool.households_with_tool),
            selectinload(Tool.recipes).joinedload(RecipeModel.recipe_category),
            selectinload(Tool.recipes).joinedload(RecipeModel.tags),
            selectinload(Tool.recipes).joinedload(RecipeModel.tools),
        ]


from .recipe import RecipeSummary  # noqa: E402

ToolWithRecipes.model_rebuild()
