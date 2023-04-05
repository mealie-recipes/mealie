from pydantic import UUID4
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
    slug: str

    class Config:
        orm_mode = True


class CategoryOut(CategoryBase):
    slug: str
    group_id: UUID4

    class Config:
        orm_mode = True


class RecipeCategoryResponse(CategoryBase):
    recipes: "list[RecipeSummary]" = []

    class Config:
        orm_mode = True


class TagIn(CategoryIn):
    pass


class TagSave(TagIn):
    group_id: UUID4


class TagBase(CategoryBase):
    pass


class TagOut(TagSave):
    id: UUID4
    slug: str

    class Config:
        orm_mode = True


class RecipeTagResponse(RecipeCategoryResponse):
    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(Tag.recipes).joinedload(RecipeModel.recipe_category),
            selectinload(Tag.recipes).joinedload(RecipeModel.tags),
            selectinload(Tag.recipes).joinedload(RecipeModel.tools),
        ]


from mealie.schema.recipe.recipe import RecipeSummary  # noqa: E402

RecipeCategoryResponse.update_forward_refs()
RecipeTagResponse.update_forward_refs()
