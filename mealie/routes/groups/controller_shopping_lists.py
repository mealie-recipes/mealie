import json
from functools import cached_property

from fastapi import APIRouter, Depends, Query
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema.group.group_shopping_list import (
    ShoppingListCreate,
    ShoppingListItemCreate,
    ShoppingListItemOut,
    ShoppingListItemUpdate,
    ShoppingListOut,
    ShoppingListSave,
    ShoppingListSummary,
    ShoppingListUpdate,
)
from mealie.schema.mapper import cast
from mealie.schema.query import GetAll
from mealie.schema.response.responses import SuccessResponse
from mealie.services.event_bus_service.event_bus_service import EventBusService
from mealie.services.event_bus_service.message_types import EventTypes
from mealie.services.group_services.shopping_lists import ShoppingListService

item_router = APIRouter(prefix="/groups/shopping/items", tags=["Group: Shopping List Items"])


@controller(item_router)
class ShoppingListItemController(BaseUserController):

    event_bus: EventBusService = Depends(EventBusService)

    @cached_property
    def service(self):
        return ShoppingListService(self.repos)

    @cached_property
    def repo(self):
        return self.deps.repos.group_shopping_list_item

    @cached_property
    def mixins(self):
        return HttpRepo[ShoppingListItemCreate, ShoppingListItemOut, ShoppingListItemCreate](
            self.repo,
            self.deps.logger,
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
        return self.mixins.create_one(data)

    @item_router.get("/{item_id}", response_model=ShoppingListItemOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @item_router.put("/{item_id}", response_model=ShoppingListItemOut)
    def update_one(self, item_id: UUID4, data: ShoppingListItemUpdate):
        return self.mixins.update_one(data, item_id)

    @item_router.delete("/{item_id}", response_model=ShoppingListItemOut)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)  # type: ignore


router = APIRouter(prefix="/groups/shopping/lists", tags=["Group: Shopping Lists"])


@controller(router)
class ShoppingListController(BaseUserController):
    event_bus: EventBusService = Depends(EventBusService)

    @cached_property
    def service(self):
        return ShoppingListService(self.repos)

    @cached_property
    def repo(self):
        return self.deps.repos.group_shopping_lists.by_group(self.deps.acting_user.group_id)

    # =======================================================================
    # CRUD Operations

    @cached_property
    def mixins(self) -> HttpRepo[ShoppingListCreate, ShoppingListOut, ShoppingListSave]:
        return HttpRepo(self.repo, self.deps.logger, self.registered_exceptions, "An unexpected error occurred.")

    @router.get("", response_model=list[ShoppingListSummary])
    def get_all(self, q: GetAll = Depends(GetAll)):
        return self.repo.get_all(start=q.start, limit=q.limit, override=ShoppingListSummary)

    @router.post("", response_model=ShoppingListOut, status_code=201)
    def create_one(self, data: ShoppingListCreate):
        save_data = cast(data, ShoppingListSave, group_id=self.deps.acting_user.group_id)
        val = self.mixins.create_one(save_data)

        if val:
            self.event_bus.dispatch(
                self.deps.acting_user.group_id,
                EventTypes.shopping_list_created,
                msg=self.t("notifications.generic-created", name=val.name),
                event_source=json.dumps(
                    {
                        "event_type": "create",
                        "item_type": "shopping-list",
                        "item_id": str(val.id),
                    }
                ),
            )

        return val

    @router.get("/{item_id}", response_model=ShoppingListOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=ShoppingListOut)
    def update_one(self, item_id: UUID4, data: ShoppingListUpdate):
        data = self.mixins.update_one(data, item_id)  # type: ignore
        if data:
            self.event_bus.dispatch(
                self.deps.acting_user.group_id,
                EventTypes.shopping_list_updated,
                msg=self.t("notifications.generic-updated", name=data.name),
                event_source=json.dumps(
                    {
                        "event_type": "update",
                        "item_type": "shopping-list",
                        "item_id": str(data.id),
                    }
                ),
            )
        return data

    @router.delete("/{item_id}", response_model=ShoppingListOut)
    def delete_one(self, item_id: UUID4):
        data = self.mixins.delete_one(item_id)  # type: ignore
        if data:
            self.event_bus.dispatch(
                self.deps.acting_user.group_id,
                EventTypes.shopping_list_deleted,
                msg=self.t("notifications.generic-deleted", name=data.name),
                event_source=json.dumps(
                    {
                        "event_type": "delete",
                        "item_type": "shopping-list",
                        "item_id": str(data.id),
                    }
                ),
            )
        return data

    # =======================================================================
    # Other Operations

    @router.post("/{item_id}/recipe/{recipe_id}", response_model=ShoppingListOut)
    def add_recipe_ingredients_to_list(self, item_id: UUID4, recipe_id: UUID4):
        return self.service.add_recipe_ingredients_to_list(item_id, recipe_id)

    @router.delete("/{item_id}/recipe/{recipe_id}", response_model=ShoppingListOut)
    def remove_recipe_ingredients_from_list(self, item_id: UUID4, recipe_id: UUID4):
        return self.service.remove_recipe_ingredients_from_list(item_id, recipe_id)
