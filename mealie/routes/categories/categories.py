from functools import cached_property

from fastapi import APIRouter
from pydantic import BaseModel

from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.mixins import CrudMixins
from mealie.schema.recipe import CategoryIn, RecipeCategoryResponse
from mealie.schema.recipe.recipe_category import CategoryBase

router = APIRouter(prefix="/categories", tags=["Categories: CRUD"])


class CategorySummary(BaseModel):
    slug: str
    name: str

    class Config:
        orm_mode = True


@controller(router)
class RecipeCategoryController(BaseUserController):
    # =========================================================================
    # CRUD Operations

    @cached_property
    def mixins(self):
        return CrudMixins(self.repos.categories, self.deps.logger)

    @router.get("", response_model=list[CategorySummary])
    def get_all(self):
        """Returns a list of available categories in the database"""
        return self.repos.categories.get_all_limit_columns(fields=["slug", "name"])

    @router.post("", status_code=201)
    def create_one(self, category: CategoryIn):
        """Creates a Category in the database"""
        return self.mixins.create_one(category)

    @router.get("/{slug}", response_model=RecipeCategoryResponse)
    def get_all_recipes_by_category(self, slug: str):
        """Returns a list of recipes associated with the provided category."""
        category_obj = self.repos.categories.get(slug)
        category_obj = RecipeCategoryResponse.from_orm(category_obj)
        return category_obj

    @router.put("/{slug}", response_model=RecipeCategoryResponse)
    def update_one(self, slug: str, update_data: CategoryIn):
        """Updates an existing Tag in the database"""
        return self.mixins.update_one(update_data, slug)

    @router.delete("/{slug}")
    def delete_one(self, slug: str):
        """
        Removes a recipe category from the database. Deleting a
        category does not impact a recipe. The category will be removed
        from any recipes that contain it
        """
        self.mixins.delete_one(slug)

    # =========================================================================
    # Read All Operations

    @router.get("/empty", response_model=list[CategoryBase])
    def get_all_empty(self):
        """Returns a list of categories that do not contain any recipes"""
        return self.repos.categories.get_empty()
