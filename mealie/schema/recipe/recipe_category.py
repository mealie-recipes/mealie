from pydantic import UUID4, ConfigDict
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.recipe import RecipeModel, Tag
from mealie.schema._mealie import MealieModel


class CategoryIn(MealieModel):
    name: str


class CategorySave(CategoryIn):
    group_id: UUID4


class CategoryBase(CategoryIn):
    id: UUID4
    group_id: UUID4 | None = None
    slug: str
    model_config = ConfigDict(from_attributes=True)


class CategoryOut(CategoryBase):
    slug: str
    group_id: UUID4
    recipe_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class CategoryMerge(MealieModel):
    from_id: UUID4
    to_id: UUID4


class RecipeCategoryResponse(CategoryBase):
    recipes: "list[RecipeSummary]" = []
    model_config = ConfigDict(from_attributes=True)


class TagIn(CategoryIn):
    pass


class TagSave(TagIn):
    group_id: UUID4


class TagBase(CategoryBase):
    pass


class TagOut(TagSave):
    id: UUID4
    slug: str
    recipe_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class TagMerge(MealieModel):
    from_id: UUID4
    to_id: UUID4


class TagRecipesRemove(MealieModel):
    recipe_ids: list[UUID4]


class RecipeTagResponse(RecipeCategoryResponse):
    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(Tag.recipes).joinedload(RecipeModel.recipe_category),
            selectinload(Tag.recipes).joinedload(RecipeModel.tags),
            selectinload(Tag.recipes).joinedload(RecipeModel.tools),
        ]


from mealie.schema.recipe.recipe import RecipeSummary  # noqa: E402

RecipeCategoryResponse.model_rebuild()
RecipeTagResponse.model_rebuild()
