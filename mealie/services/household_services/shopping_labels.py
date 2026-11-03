from pydantic import UUID4
from sqlalchemy import case

from mealie.core.exceptions import UnexpectedNone
from mealie.db.models.household.shopping_list import ShoppingListItem
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.group_shopping_list import (
    ItemPositionChange,
    ShoppingLabelCreate,
    ShoppingLabelOut,
    ShoppingLabelSave,
    ShoppingLabelUpdate,
    ShoppingListItemPositionUpdate,
    ShoppingListItemsCollectionOut,
    ShoppingListItemUpdateBulk,
)
from mealie.schema.response.pagination import PaginationQuery


class ShoppingLabelService:
    def __init__(self, repos: AllRepositories):
        self.repos = repos
        self.shopping_labels = repos.household_shopping_labels
        self.list_items = repos.group_shopping_list_item
        self.shopping_lists = repos.group_shopping_lists

    def create_one(self, data: ShoppingLabelCreate) -> ShoppingLabelOut:
        """Create a new shopping label for the household"""
        save_data = data.cast(ShoppingLabelSave, household_id=self.repos.household_id)
        new_label = self.shopping_labels.create(save_data)
        return new_label

    def get_all(self, q: PaginationQuery = PaginationQuery()) -> ShoppingLabelOut:
        """Get all shopping labels for the household"""
        response = self.shopping_labels.page_all(
            pagination=q,
            override=ShoppingLabelOut,
        )
        response.set_pagination_guides("", q.model_dump())
        return response

    def get_one(self, label_id: UUID4) -> ShoppingLabelOut | None:
        """Get a single shopping label by ID"""
        return self.shopping_labels.get_one(label_id, override_schema=ShoppingLabelOut)

    def update_one(self, label_id: UUID4, data: ShoppingLabelUpdate) -> ShoppingLabelOut:
        """Update a shopping label"""
        label = self.get_one(label_id)
        if not label:
            raise UnexpectedNone("Shopping label not found")

        if label.is_system and not data.is_system:
            # Prevent making system labels non-system
            data.is_system = True

        return self.shopping_labels.update(label_id, data)

    def delete_one(self, label_id: UUID4) -> ShoppingLabelOut | None:
        """Delete a shopping label (only if not system)"""
        label = self.get_one(label_id)
        if not label:
            raise UnexpectedNone("Shopping label not found")

        if label.is_system:
            raise ValueError("Cannot delete system labels")

        # Set label_id to NULL on associated items
        self.repos.session.execute(
            ShoppingListItem.__table__.update()
            .where(ShoppingListItem.shopping_label_id == label_id)
            .values(shopping_label_id=None)
        )

        return self.shopping_labels.delete(label_id)

    def update_item(self, item_id: UUID4, data: ShoppingListItemPositionUpdate) -> ShoppingListItemsCollectionOut:
        """Update a single item's position and/or label"""
        item = self.list_items.get_one(item_id)
        if not item:
            raise UnexpectedNone("Shopping list item not found")

        # Build update data
        update_data = item.cast(ShoppingListItemUpdateBulk, id=item_id)

        if data.position is not None:
            update_data.position = data.position

        if "shopping_label_id" in data.model_fields_set:
            update_data.shopping_label_id = data.shopping_label_id

        # Use existing bulk update logic
        from mealie.services.household_services.shopping_lists import ShoppingListService

        shopping_service = ShoppingListService(self.repos)
        return shopping_service.bulk_update_items([update_data])

    def reorder_items(self, list_id: UUID4, changes: list[ItemPositionChange]) -> None:
        """Bulk reorder items in a single transaction"""
        if not self.shopping_lists.get_one(list_id):
            raise UnexpectedNone("Shopping list not found")

        if not changes:
            return

        # Build CASE WHEN statement for bulk position update
        case_conditions = []
        item_ids = []
        label_updates = []

        for change in changes:
            item_ids.append(change.item_id)
            case_conditions.append((ShoppingListItem.id == change.item_id, change.position))
            if change.label_id is not None:
                label_updates.append((ShoppingListItem.id == change.item_id, change.label_id))

        # Update positions in bulk
        position_case = case(*case_conditions, else_=ShoppingListItem.position)
        self.repos.session.execute(
            ShoppingListItem.__table__.update()
            .where(ShoppingListItem.id.in_(item_ids), ShoppingListItem.shopping_list_id == list_id)
            .values(position=position_case)
        )

        # Update labels in bulk if any
        if label_updates:
            label_case = case(*label_updates, else_=ShoppingListItem.shopping_label_id)
            self.repos.session.execute(
                ShoppingListItem.__table__.update()
                .where(ShoppingListItem.id.in_(item_ids), ShoppingListItem.shopping_list_id == list_id)
                .values(shopping_label_id=label_case)
            )

        self.repos.session.commit()
