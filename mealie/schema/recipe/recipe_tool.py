from pydantic import UUID4, ConfigDict
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.schema._mealie import MealieModel

from ...db.models.recipe import RecipeModel, Tool


class RecipeToolCreate(MealieModel):
    name: str
    on_hand: bool = False


class RecipeToolSave(RecipeToolCreate):
    group_id: UUID4


class RecipeToolOut(RecipeToolCreate):
    id: UUID4
    slug: str
    model_config = ConfigDict(from_attributes=True)


class RecipeToolResponse(RecipeToolOut):
    recipes: list["RecipeSummary"] = []
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(Tool.recipes).joinedload(RecipeModel.recipe_category),
            selectinload(Tool.recipes).joinedload(RecipeModel.tags),
            selectinload(Tool.recipes).joinedload(RecipeModel.tools),
        ]


from .recipe import RecipeSummary  # noqa: E402

RecipeToolResponse.model_rebuild()
