from pydantic import ConfigDict
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.recipe import RecipeModel, Tag

from .recipe_organizers import CategoryOut, TagOut


class CategoryWithRecipes(CategoryOut):
    recipes: list[RecipeSummary] = []
    model_config = ConfigDict(from_attributes=True)


class TagWithRecipes(TagOut):
    recipes: list[RecipeSummary] = []
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(Tag.recipes).joinedload(RecipeModel.recipe_category),
            selectinload(Tag.recipes).joinedload(RecipeModel.tags),
            selectinload(Tag.recipes).joinedload(RecipeModel.tools),
        ]


from mealie.schema.recipe.recipe import RecipeSummary  # noqa: E402

CategoryWithRecipes.model_rebuild()
TagWithRecipes.model_rebuild()
