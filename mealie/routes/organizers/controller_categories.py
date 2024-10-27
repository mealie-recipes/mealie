from functools import cached_property

from fastapi import APIRouter, Depends
from pydantic import UUID4, BaseModel, ConfigDict

from mealie.routes._base import BaseCrudController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema import mapper
from mealie.schema.recipe import CategoryIn, RecipeCategoryResponse
from mealie.schema.recipe.recipe import RecipeCategory, RecipeCategoryPagination
from mealie.schema.recipe.recipe_category import CategoryBase, CategoryOut, CategorySave
from mealie.schema.response.pagination import PaginationQuery
from mealie.services import urls
from mealie.services.event_bus_service.event_types import EventCategoryData, EventOperation, EventTypes

router = APIRouter(prefix="/categories", tags=["Organizer: Categories"])


class CategorySummary(BaseModel):
    id: UUID4
    slug: str
    name: str
    model_config = ConfigDict(from_attributes=True)


@controller(router)
class RecipeCategoryController(BaseCrudController):
    # =========================================================================
    # CRUD Operations
    @cached_property
    def repo(self):
        return self.repos.categories

    @cached_property
    def mixins(self):
        return HttpRepo[CategorySave, CategoryOut, CategorySave](self.repo, self.logger)

    @router.get("", response_model=RecipeCategoryPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery), search: str | None = None):
        """Returns a list of available categories in the database"""
        response = self.repo.page_all(
            pagination=q,
            override=RecipeCategory,
            search=search,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", status_code=201)
    def create_one(self, category: CategoryIn):
        """Creates a Category in the database"""
        save_data = mapper.cast(category, CategorySave, group_id=self.group_id)
        new_category = self.mixins.create_one(save_data)
        if new_category:
            self.publish_event(
                event_type=EventTypes.category_created,
                document_data=EventCategoryData(operation=EventOperation.create, category_id=new_category.id),
                group_id=new_category.group_id,
                household_id=None,
                message=self.t(
                    "notifications.generic-created-with-url",
                    name=new_category.name,
                    url=urls.category_url(new_category.slug, self.settings.BASE_URL),
                ),
            )

        return new_category

    @router.get("/empty", response_model=list[CategoryBase])
    def get_all_empty(self):
        """Returns a list of categories that do not contain any recipes"""
        return self.repos.categories.get_empty()

    @router.get("/{item_id}", response_model=CategorySummary)
    def get_one(self, item_id: UUID4):
        """Returns a list of recipes associated with the provided category."""
        category_obj = self.mixins.get_one(item_id)
        category_obj = CategorySummary.model_validate(category_obj)
        return category_obj

    @router.put("/{item_id}", response_model=CategorySummary)
    def update_one(self, item_id: UUID4, update_data: CategoryIn):
        """Updates an existing Tag in the database"""
        save_data = mapper.cast(update_data, CategorySave, group_id=self.group_id)
        category = self.mixins.update_one(save_data, item_id)

        if category:
            self.publish_event(
                event_type=EventTypes.category_updated,
                document_data=EventCategoryData(operation=EventOperation.update, category_id=category.id),
                group_id=category.group_id,
                household_id=None,
                message=self.t(
                    "notifications.generic-updated-with-url",
                    name=category.name,
                    url=urls.category_url(category.slug, self.settings.BASE_URL),
                ),
            )

        return category

    @router.delete("/{item_id}")
    def delete_one(self, item_id: UUID4):
        """
        Removes a recipe category from the database. Deleting a
        category does not impact a recipe. The category will be removed
        from any recipes that contain it
        """
        if category := self.mixins.delete_one(item_id):
            self.publish_event(
                event_type=EventTypes.category_deleted,
                document_data=EventCategoryData(operation=EventOperation.delete, category_id=category.id),
                group_id=category.group_id,
                household_id=None,
                message=self.t("notifications.generic-deleted", name=category.name),
            )

    # =========================================================================
    # Read All Operations

    @router.get("/slug/{category_slug}")
    def get_one_by_slug(self, category_slug: str):
        """Returns a category object with the associated recieps relating to the category"""
        category: RecipeCategory = self.mixins.get_one(category_slug, "slug")
        return RecipeCategoryResponse.model_construct(
            id=category.id,
            slug=category.slug,
            name=category.name,
            recipes=self.repos.recipes.get_by_categories([category]),
        )
