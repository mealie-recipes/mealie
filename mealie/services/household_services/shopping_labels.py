from pydantic import UUID4
from sqlalchemy import case, select

from mealie.core.exceptions import UnexpectedNone
from mealie.db.models.household.shopping_list import ShoppingListItem, ShoppingListMultiPurposeLabel
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.group_shopping_list import (
    ItemPositionChange,
    ShoppingLabelCreate,
    ShoppingLabelOut,
    ShoppingLabelSave,
    ShoppingLabelUpdate,
    ShoppingListItemOut,
    ShoppingListItemPositionUpdate,
    ShoppingListItemsCollectionOut,
    ShoppingListItemUpdateBulk,
)
from mealie.schema.response.pagination import PaginationQuery


class ShoppingLabelService:
    DEFAULT_SYSTEM_LABELS = [
        {"name": "Meat & Seafood", "color": "#C62828", "sort_order": 1, "is_system": True},
        {"name": "Produce", "color": "#2E7D32", "sort_order": 2, "is_system": True},
        {"name": "Pantry \u2014 Canned/Jarred", "color": "#F57F17", "sort_order": 3, "is_system": True},
        {"name": "Pantry \u2014 Dry Goods", "color": "#E65100", "sort_order": 4, "is_system": True},
        {"name": "Pantry \u2014 Spices", "color": "#6D4C41", "sort_order": 5, "is_system": True},
        {"name": "Oils & Vinegars", "color": "#F9A825", "sort_order": 6, "is_system": True},
        {"name": "Dairy & Eggs", "color": "#1565C0", "sort_order": 7, "is_system": True},
        {"name": "Frozen / Bread", "color": "#455A64", "sort_order": 8, "is_system": True},
        {"name": "Other", "color": "#757575", "sort_order": 99, "is_system": True},
    ]

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

    def ensure_system_labels(self) -> list[ShoppingLabelOut]:
        """Ensure default system labels exist for the household"""
        existing_labels = self.get_all(PaginationQuery(per_page=-1))
        existing_names = {label.name for label in existing_labels.items}

        created_labels = []
        for sys_label in self.DEFAULT_SYSTEM_LABELS:
            if sys_label["name"] not in existing_names:
                create_data = ShoppingLabelCreate(**sys_label)
                new_label = self.create_one(create_data)
                created_labels.append(new_label)

        return created_labels

    def seed_system_labels_for_list(self, list_id: UUID4) -> None:
        """Seed system labels for a new shopping list"""
        labels = self.ensure_system_labels()

        # Create label settings for the list
        label_settings = [
            ShoppingListMultiPurposeLabelCreate(
                shopping_list_id=list_id,
                label_id=label.id,
                position=label.sort_order,
            )
            for label in labels
        ]

        # Check if settings already exist
        existing = (
            self.repos.session.execute(
                select(ShoppingListMultiPurposeLabel).where(ShoppingListMultiPurposeLabel.shopping_list_id == list_id)
            )
            .scalars()
            .all()
        )

        if not existing:
            self.repos.session.bulk_save_objects(
                [ShoppingListMultiPurposeLabel(**setting.model_dump()) for setting in label_settings]
            )
            self.repos.session.commit()

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
        if not changes:
            return

        if not self.shopping_lists.get_one(list_id):
            raise UnexpectedNone("Shopping list not found")

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

    def shift_positions(self, list_id: UUID4, start_position: int, shift_by: int = 1) -> None:
        """Shift positions of items at or after start_position"""
        self.repos.session.execute(
            ShoppingListItem.__table__.update()
            .where(
                ShoppingListItem.shopping_list_id == list_id,
                ShoppingListItem.position >= start_position,
            )
            .values(position=ShoppingListItem.position + shift_by)
        )
        self.repos.session.commit()

    def insert_item_at_position(
        self, list_id: UUID4, position: int, item_data: ShoppingListItemUpdateBulk
    ) -> ShoppingListItemOut:
        """Insert an item at a specific position, shifting others"""
        # Shift existing items
        self.shift_positions(list_id, position, 1)

        # Set the item's position
        item_data.position = position
        item_data.shopping_list_id = list_id

        # Create the item
        from mealie.services.household_services.shopping_lists import ShoppingListService

        shopping_service = ShoppingListService(self.repos)
        result = shopping_service.bulk_create_items([item_data])
        return result.created_items[0] if result.created_items else None


class ShoppingListMultiPurposeLabelCreate:
    """Helper class for creating label settings"""

    def __init__(self, shopping_list_id: UUID4, label_id: UUID4, position: int):
        self.shopping_list_id = shopping_list_id
        self.label_id = label_id
        self.position = position

    def model_dump(self):
        return {
            "shopping_list_id": self.shopping_list_id,
            "label_id": self.label_id,
            "position": self.position,
        }
