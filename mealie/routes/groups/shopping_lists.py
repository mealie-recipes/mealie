from functools import cached_property
from sqlite3 import IntegrityError
from typing import Type

from fastapi import APIRouter, Depends
from pydantic import UUID4

from mealie.routes._base.controller import controller
from mealie.routes._base.dependencies import SharedDependencies
from mealie.routes._base.mixins import CrudMixins
from mealie.schema.group.group_shopping_list import (
    ShoppingListCreate,
    ShoppingListOut,
    ShoppingListSave,
    ShoppingListSummary,
    ShoppingListUpdate,
)
from mealie.schema.mapper import cast
from mealie.schema.query import GetAll
from mealie.services.event_bus_service.event_bus_service import EventBusService
from mealie.services.event_bus_service.message_types import EventTypes
from mealie.services.group_services.shopping_lists import ShoppingListService

router = APIRouter(prefix="/groups/shopping/lists", tags=["Group: Shopping Lists"])


@controller(router)
class ShoppingListRoutes:
    deps: SharedDependencies = Depends(SharedDependencies.user)
    service: ShoppingListService = Depends(ShoppingListService.private)
    event_bus: EventBusService = Depends(EventBusService)

    @cached_property
    def repo(self):
        if not self.deps.acting_user:
            raise Exception("No user is logged in.")

        return self.deps.repos.group_shopping_lists.by_group(self.deps.acting_user.group_id)

    def registered_exceptions(self, ex: Type[Exception]) -> str:
        registered = {
            Exception: "An unexpected error occurred.",
            IntegrityError: "An unexpected error occurred.",
        }

        return registered.get(ex, "An unexpected error occurred.")

    # =======================================================================
    # CRUD Operations

    @property
    def mixins(self) -> CrudMixins:
        return CrudMixins(self.repo, self.deps.logger, self.registered_exceptions, "An unexpected error occurred.")

    @router.get("", response_model=list[ShoppingListSummary])
    def get_all(self, q: GetAll = Depends(GetAll)):
        return self.repo.get_all(start=q.start, limit=q.limit, override_schema=ShoppingListSummary)

    @router.post("", response_model=ShoppingListOut)
    def create_one(self, data: ShoppingListCreate):
        save_data = cast(data, ShoppingListSave, group_id=self.deps.acting_user.group_id)
        val = self.mixins.create_one(save_data)

        if val:
            self.event_bus.dispatch(
                self.deps.acting_user.group_id,
                EventTypes.shopping_list_created,
                msg="A new shopping list has been created.",
            )

        return val

    @router.get("/{item_id}", response_model=ShoppingListOut)
    def get_one(self, item_id: UUID4):
        return self.repo.get_one(item_id)

    @router.put("/{item_id}", response_model=ShoppingListOut)
    def update_one(self, item_id: UUID4, data: ShoppingListUpdate):
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=ShoppingListOut)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)  # type: ignore

    # =======================================================================
    # Other Operations

    @router.post("/{item_id}/recipe/{recipe_id}", response_model=ShoppingListOut)
    def add_recipe_ingredients_to_list(self, item_id: UUID4, recipe_id: int):
        return self.service.add_recipe_ingredients_to_list(item_id, recipe_id)

    @router.delete("/{item_id}/recipe/{recipe_id}", response_model=ShoppingListOut)
    def remove_recipe_ingredients_from_list(self, item_id: UUID4, recipe_id: int):
        return self.service.remove_recipe_ingredients_from_list(item_id, recipe_id)
