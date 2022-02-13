from functools import cached_property

from fastapi import APIRouter
from pydantic import UUID4, BaseModel

from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.mixins import CrudMixins
from mealie.schema import mapper
from mealie.schema.recipe import CategoryIn, RecipeCategoryResponse
from mealie.schema.recipe.recipe import RecipeCategory
from mealie.schema.recipe.recipe_category import CategoryBase, CategorySave

router = APIRouter(prefix="/categories", tags=["Organizer: Categories"])


class CategorySummary(BaseModel):
    id: UUID4
    slug: str
    name: str

    class Config:
        orm_mode = True


@controller(router)
class RecipeCategoryController(BaseUserController):
    # =========================================================================
    # CRUD Operations
    @cached_property
    def repo(self):
        return self.repos.categories.by_group(self.group_id)

    @cached_property
    def mixins(self):
        return CrudMixins(self.repo, self.deps.logger)

    @router.get("", response_model=list[CategorySummary])
    def get_all(self):
        """Returns a list of available categories in the database"""
        return self.repo.get_all(override_schema=CategorySummary)

    @router.post("", status_code=201)
    def create_one(self, category: CategoryIn):
        """Creates a Category in the database"""
        save_data = mapper.cast(category, CategorySave, group_id=self.group_id)
        return self.mixins.create_one(save_data)

    @router.get("/{item_id}", response_model=CategorySummary)
    def get_one(self, item_id: UUID4):
        """Returns a list of recipes associated with the provided category."""
        category_obj = self.mixins.get_one(item_id)
        category_obj = CategorySummary.from_orm(category_obj)
        return category_obj

    @router.put("/{item_id}", response_model=CategorySummary)
    def update_one(self, item_id: UUID4, update_data: CategoryIn):
        """Updates an existing Tag in the database"""
        save_data = mapper.cast(update_data, CategorySave, group_id=self.group_id)
        return self.mixins.update_one(save_data, item_id)

    @router.delete("/{item_id}")
    def delete_one(self, item_id: UUID4):
        """
        Removes a recipe category from the database. Deleting a
        category does not impact a recipe. The category will be removed
        from any recipes that contain it
        """
        self.mixins.delete_one(item_id)

    # =========================================================================
    # Read All Operations

    @router.get("/empty", response_model=list[CategoryBase])
    def get_all_empty(self):
        """Returns a list of categories that do not contain any recipes"""
        return self.repos.categories.get_empty()

    @router.get("/slug/{category_slug}")
    def get_one_by_slug(self, category_slug: str):
        """Returns a category object with the associated recieps relating to the category"""
        category: RecipeCategory = self.mixins.get_one(category_slug, "slug")
        return RecipeCategoryResponse.construct(
            id=category.id,
            slug=category.slug,
            name=category.name,
            recipes=self.repos.recipes.by_group(self.group_id).get_by_categories([category]),
        )
