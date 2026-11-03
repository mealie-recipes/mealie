from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError

from mealie.core.exceptions import UnexpectedNone
from mealie.routes._base import BaseCrudController, BaseUserController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.permissions import Perm, require
from mealie.schema.household.group_shopping_list import (
    ItemPositionChange,
    ShoppingLabelCreate,
    ShoppingLabelOut,
    ShoppingLabelPagination,
    ShoppingLabelUpdate,
    ShoppingListItemPositionUpdate,
    ShoppingListItemsCollectionOut,
)
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.response.responses import SuccessResponse
from mealie.services.household_services.shopping_labels import ShoppingLabelService

router = APIRouter(prefix="/households/shopping/labels", tags=["Households: Shopping Labels"])


@controller(router)
class ShoppingLabelController(BaseCrudController):
    @cached_property
    def service(self):
        return ShoppingLabelService(self.repos)

    @cached_property
    def repo(self):
        return self.repos.household_shopping_labels

    @cached_property
    def mixins(self):
        return HttpRepo(self.repo, self.logger)

    @router.get("", response_model=ShoppingLabelPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        """Get all shopping labels for the household"""
        return self.service.get_all(q)

    @router.post("", response_model=ShoppingLabelOut, status_code=201, dependencies=[require(Perm.GROUP_ORGANIZE)])
    def create_one(self, data: ShoppingLabelCreate):
        """Create a new shopping label"""
        try:
            return self.service.create_one(data)
        except IntegrityError:
            self.repos.session.rollback()
            raise HTTPException(status_code=409, detail="A shopping label with that name already exists") from None

    @router.get("/{label_id}", response_model=ShoppingLabelOut)
    def get_one(self, label_id: UUID4):
        """Get a single shopping label"""
        label = self.service.get_one(label_id)
        if not label:
            raise HTTPException(status_code=404, detail="Shopping label not found")
        return label

    @router.put("/{label_id}", response_model=ShoppingLabelOut, dependencies=[require(Perm.GROUP_ORGANIZE)])
    def update_one(self, label_id: UUID4, data: ShoppingLabelUpdate):
        """Update a shopping label"""
        label = self.service.get_one(label_id)
        if not label:
            raise HTTPException(status_code=404, detail="Shopping label not found")

        if label.is_system and not data.is_system:
            raise HTTPException(status_code=403, detail="Cannot modify system label properties")

        try:
            return self.service.update_one(label_id, data)
        except IntegrityError:
            self.repos.session.rollback()
            raise HTTPException(status_code=409, detail="A shopping label with that name already exists") from None

    @router.delete("/{label_id}", response_model=ShoppingLabelOut, dependencies=[require(Perm.GROUP_ORGANIZE)])
    def delete_one(self, label_id: UUID4):
        """Delete a shopping label (system labels cannot be deleted)"""
        label = self.service.get_one(label_id)
        if not label:
            raise HTTPException(status_code=404, detail="Shopping label not found")

        if label.is_system:
            raise HTTPException(status_code=403, detail="Cannot delete system labels")

        return self.service.delete_one(label_id)


# Item PATCH endpoints
item_router = APIRouter(prefix="/households/shopping/items", tags=["Households: Shopping List Items"])


@controller(item_router)
class ShoppingListItemLabelController(BaseUserController):
    @cached_property
    def service(self):
        return ShoppingLabelService(self.repos)

    @cached_property
    def list_items_repo(self):
        return self.repos.group_shopping_list_item

    @item_router.patch("/{item_id}", response_model=ShoppingListItemsCollectionOut)
    def update_item(self, item_id: UUID4, data: ShoppingListItemPositionUpdate):
        """Update item position and/or label"""
        try:
            return self.service.update_item(item_id, data)
        except UnexpectedNone:
            raise HTTPException(status_code=404, detail="Shopping list item not found") from None


# Bulk reorder endpoint
list_router = APIRouter(prefix="/households/shopping/lists", tags=["Households: Shopping Lists"])


@controller(list_router)
class ShoppingListReorderController(BaseUserController):
    @cached_property
    def service(self):
        return ShoppingLabelService(self.repos)

    @list_router.patch("/{list_id}/reorder", response_model=SuccessResponse)
    def reorder_items(self, list_id: UUID4, changes: list[ItemPositionChange]):
        """Bulk reorder items in a shopping list"""
        try:
            self.service.reorder_items(list_id, changes)
        except UnexpectedNone:
            raise HTTPException(status_code=404, detail="Shopping list not found") from None
        return SuccessResponse.respond()
