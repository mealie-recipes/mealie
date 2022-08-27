from functools import cached_property

from fastapi import APIRouter, Depends, Query
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseCrudController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema.group.group_shopping_list import (
    ShoppingListCreate,
    ShoppingListItemCreate,
    ShoppingListItemOut,
    ShoppingListItemUpdate,
    ShoppingListOut,
    ShoppingListPagination,
    ShoppingListSave,
    ShoppingListSummary,
    ShoppingListUpdate,
)
from mealie.schema.mapper import cast
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.response.responses import SuccessResponse
from mealie.services.event_bus_service.event_types import (
    EventOperation,
    EventShoppingListData,
    EventShoppingListItemBulkData,
    EventShoppingListItemData,
    EventTypes,
)
from mealie.services.group_services.shopping_lists import ShoppingListService

item_router = APIRouter(prefix="/groups/shopping/items", tags=["Group: Shopping List Items"])


@controller(item_router)
class ShoppingListItemController(BaseCrudController):
    @cached_property
    def service(self):
        return ShoppingListService(self.repos)

    @cached_property
    def repo(self):
        return self.repos.group_shopping_list_item

    @cached_property
    def mixins(self):
        return HttpRepo[ShoppingListItemCreate, ShoppingListItemOut, ShoppingListItemCreate](
            self.repo,
            self.logger,
        )

    @item_router.put("", response_model=list[ShoppingListItemOut])
    def update_many(self, data: list[ShoppingListItemUpdate]):
        # TODO: Convert to update many with single call

        all_updates = []
        keep_ids = []

        for item in self.service.consolidate_list_items(data):
            updated_data = self.mixins.update_one(item, item.id)
            all_updates.append(updated_data)
            keep_ids.append(updated_data.id)

        for item in data:
            if item.id not in keep_ids:
                self.mixins.delete_one(item.id)

        return all_updates

    @item_router.delete("", response_model=SuccessResponse)
    def delete_many(self, ids: list[UUID4] = Query(None)):
        x = 0
        for item_id in ids:
            self.mixins.delete_one(item_id)
            x += 1

        return SuccessResponse.respond(message=f"Successfully deleted {x} items")

    @item_router.post("", response_model=ShoppingListItemOut, status_code=201)
    def create_one(self, data: ShoppingListItemCreate):
        shopping_list_item = self.mixins.create_one(data)

        if shopping_list_item:
            self.publish_event(
                event_type=EventTypes.shopping_list_updated,
                document_data=EventShoppingListItemData(
                    operation=EventOperation.create,
                    shopping_list_id=shopping_list_item.shopping_list_id,
                    shopping_list_item_id=shopping_list_item.id,
                ),
                message=self.t(
                    "notifications.generic-created",
                    name=f"An item on shopping list {shopping_list_item.shopping_list_id}",
                ),
            )

        return shopping_list_item

    @item_router.get("/{item_id}", response_model=ShoppingListItemOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @item_router.put("/{item_id}", response_model=ShoppingListItemOut)
    def update_one(self, item_id: UUID4, data: ShoppingListItemUpdate):
        shopping_list_item = self.mixins.update_one(data, item_id)

        if shopping_list_item:
            self.publish_event(
                event_type=EventTypes.shopping_list_updated,
                document_data=EventShoppingListItemData(
                    operation=EventOperation.update,
                    shopping_list_id=shopping_list_item.shopping_list_id,
                    shopping_list_item_id=shopping_list_item.id,
                ),
                message=self.t(
                    "notifications.generic-updated",
                    name=f"An item on shopping list {shopping_list_item.shopping_list_id}",
                ),
            )

        return shopping_list_item

    @item_router.delete("/{item_id}", response_model=ShoppingListItemOut)
    def delete_one(self, item_id: UUID4):
        shopping_list_item = self.mixins.delete_one(item_id)  # type: ignore

        if shopping_list_item:
            self.publish_event(
                event_type=EventTypes.shopping_list_updated,
                document_data=EventShoppingListItemData(
                    operation=EventOperation.delete,
                    shopping_list_id=shopping_list_item.shopping_list_id,
                    shopping_list_item_id=shopping_list_item.id,
                ),
                message=self.t(
                    "notifications.generic-deleted",
                    name=f"An item on shopping list {shopping_list_item.shopping_list_id}",
                ),
            )

        return shopping_list_item


router = APIRouter(prefix="/groups/shopping/lists", tags=["Group: Shopping Lists"])


@controller(router)
class ShoppingListController(BaseCrudController):
    @cached_property
    def service(self):
        return ShoppingListService(self.repos)

    @cached_property
    def repo(self):
        return self.repos.group_shopping_lists.by_group(self.user.group_id)

    # =======================================================================
    # CRUD Operations

    @cached_property
    def mixins(self) -> HttpRepo[ShoppingListCreate, ShoppingListOut, ShoppingListSave]:
        return HttpRepo(self.repo, self.logger, self.registered_exceptions, "An unexpected error occurred.")

    @router.get("", response_model=ShoppingListPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=ShoppingListSummary,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.dict())
        return response

    @router.post("", response_model=ShoppingListOut, status_code=201)
    def create_one(self, data: ShoppingListCreate):
        save_data = cast(data, ShoppingListSave, group_id=self.user.group_id)
        shopping_list = self.mixins.create_one(save_data)

        if shopping_list:
            self.publish_event(
                event_type=EventTypes.shopping_list_created,
                document_data=EventShoppingListData(operation=EventOperation.create, shopping_list_id=shopping_list.id),
                message=self.t("notifications.generic-created", name=shopping_list.name),
            )

        return shopping_list

    @router.get("/{item_id}", response_model=ShoppingListOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=ShoppingListOut)
    def update_one(self, item_id: UUID4, data: ShoppingListUpdate):
        shopping_list = self.mixins.update_one(data, item_id)  # type: ignore

        if shopping_list:
            self.publish_event(
                event_type=EventTypes.shopping_list_updated,
                document_data=EventShoppingListData(operation=EventOperation.update, shopping_list_id=shopping_list.id),
                message=self.t("notifications.generic-updated", name=shopping_list.name),
            )

        return shopping_list

    @router.delete("/{item_id}", response_model=ShoppingListOut)
    def delete_one(self, item_id: UUID4):
        shopping_list = self.mixins.delete_one(item_id)  # type: ignore
        if shopping_list:
            self.publish_event(
                event_type=EventTypes.shopping_list_deleted,
                document_data=EventShoppingListData(operation=EventOperation.delete, shopping_list_id=shopping_list.id),
                message=self.t("notifications.generic-deleted", name=shopping_list.name),
            )

        return shopping_list

    # =======================================================================
    # Other Operations

    @router.post("/{item_id}/recipe/{recipe_id}", response_model=ShoppingListOut)
    def add_recipe_ingredients_to_list(self, item_id: UUID4, recipe_id: UUID4):
        (
            shopping_list,
            new_shopping_list_items,
            updated_shopping_list_items,
            deleted_shopping_list_items,
        ) = self.service.add_recipe_ingredients_to_list(item_id, recipe_id)

        if new_shopping_list_items:
            self.publish_event(
                event_type=EventTypes.shopping_list_updated,
                document_data=EventShoppingListItemBulkData(
                    operation=EventOperation.create,
                    shopping_list_id=shopping_list.id,
                    shopping_list_item_ids=[shopping_list_item.id for shopping_list_item in new_shopping_list_items],
                ),
            )

        if updated_shopping_list_items:
            self.publish_event(
                event_type=EventTypes.shopping_list_updated,
                document_data=EventShoppingListItemBulkData(
                    operation=EventOperation.update,
                    shopping_list_id=shopping_list.id,
                    shopping_list_item_ids=[
                        shopping_list_item.id for shopping_list_item in updated_shopping_list_items
                    ],
                ),
            )

        if deleted_shopping_list_items:
            self.publish_event(
                event_type=EventTypes.shopping_list_updated,
                document_data=EventShoppingListItemBulkData(
                    operation=EventOperation.delete,
                    shopping_list_id=shopping_list.id,
                    shopping_list_item_ids=[
                        shopping_list_item.id for shopping_list_item in deleted_shopping_list_items
                    ],
                ),
            )

        return shopping_list

    @router.delete("/{item_id}/recipe/{recipe_id}", response_model=ShoppingListOut)
    def remove_recipe_ingredients_from_list(self, item_id: UUID4, recipe_id: UUID4):
        (
            shopping_list,
            updated_shopping_list_items,
            deleted_shopping_list_items,
        ) = self.service.remove_recipe_ingredients_from_list(item_id, recipe_id)

        if updated_shopping_list_items:
            self.publish_event(
                event_type=EventTypes.shopping_list_updated,
                document_data=EventShoppingListItemBulkData(
                    operation=EventOperation.update,
                    shopping_list_id=shopping_list.id,
                    shopping_list_item_ids=[
                        shopping_list_item.id for shopping_list_item in updated_shopping_list_items
                    ],
                ),
            )

        if deleted_shopping_list_items:
            self.publish_event(
                event_type=EventTypes.shopping_list_updated,
                document_data=EventShoppingListItemBulkData(
                    operation=EventOperation.delete,
                    shopping_list_id=shopping_list.id,
                    shopping_list_item_ids=[
                        shopping_list_item.id for shopping_list_item in deleted_shopping_list_items
                    ],
                ),
            )

        return shopping_list
