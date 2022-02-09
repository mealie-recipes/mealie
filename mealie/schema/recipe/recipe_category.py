from fastapi_camelcase import CamelModel
from pydantic import UUID4
from pydantic.utils import GetterDict


class CategoryIn(CamelModel):
    name: str


class CategorySave(CategoryIn):
    group_id: UUID4


class CategoryBase(CategoryIn):
    id: int
    slug: str

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(_cls, name_orm):
            return {
                **GetterDict(name_orm),
            }


class CategoryOut(CategoryBase):
    id: int
    slug: str

    class Config:
        orm_mode = True


class RecipeCategoryResponse(CategoryBase):
    recipes: "list[Recipe]" = []

    class Config:
        orm_mode = True
        schema_extra = {"example": {"id": 1, "name": "dinner", "recipes": [{}]}}


class TagIn(CategoryIn):
    pass


class TagSave(TagIn):
    group_id: UUID4


class TagBase(CategoryBase):
    pass


class TagOut(TagSave):
    id: int
    slug: str

    class Config:
        orm_mode = True


class RecipeTagResponse(RecipeCategoryResponse):
    pass


from mealie.schema.recipe.recipe import Recipe

RecipeCategoryResponse.update_forward_refs()
RecipeTagResponse.update_forward_refs()
