import uuid
from datetime import datetime
from enum import Enum, auto
from typing import Any

from pydantic import UUID4

from ...schema._mealie.mealie_model import MealieModel

INTERNAL_INTEGRATION_ID = "mealie_generic_user"


class EventTypes(Enum):
    """
    The event type defines whether or not a subscriber should receive an event.

    Each event type is represented by a field on the subscriber repository, therefore any changes
    made here must also be reflected in the database (and likely requires a database migration).

    If you'd like more granular control over the metadata of the event, e.g. events for sub-records
    (like shopping list items), modify the event document type instead (which is not tied to a database entry).
    """

    # used internally and cannot be subscribed to
    test_message = auto()
    webhook_task = auto()

    recipe_created = auto()
    recipe_updated = auto()
    recipe_deleted = auto()

    user_signup = auto()

    data_migrations = auto()
    data_export = auto()
    data_import = auto()

    mealplan_entry_created = auto()

    shopping_list_created = auto()
    shopping_list_updated = auto()
    shopping_list_deleted = auto()

    cookbook_created = auto()
    cookbook_updated = auto()
    cookbook_deleted = auto()

    tag_created = auto()
    tag_updated = auto()
    tag_deleted = auto()

    category_created = auto()
    category_updated = auto()
    category_deleted = auto()


class EventDocumentType(Enum):
    generic = "generic"

    category = "category"
    cookbook = "cookbook"
    mealplan = "mealplan"
    shopping_list = "shopping_list"
    shopping_list_item = "shopping_list_item"
    recipe = "recipe"
    recipe_bulk_report = "recipe_bulk_report"
    recipe_timeline_event = "recipe_timeline_event"
    tag = "tag"


class EventOperation(Enum):
    info = "info"

    create = "create"
    update = "update"
    delete = "delete"


class EventDocumentDataBase(MealieModel):
    document_type: EventDocumentType
    operation: EventOperation
    ...


class EventCategoryData(EventDocumentDataBase):
    document_type = EventDocumentType.category
    category_id: UUID4


class EventCookbookData(EventDocumentDataBase):
    document_type = EventDocumentType.cookbook
    cookbook_id: UUID4


class EventCookbookBulkData(EventDocumentDataBase):
    document_type = EventDocumentType.cookbook
    cookbook_ids: list[UUID4]


class EventShoppingListData(EventDocumentDataBase):
    document_type = EventDocumentType.shopping_list
    shopping_list_id: UUID4


class EventShoppingListItemData(EventDocumentDataBase):
    document_type = EventDocumentType.shopping_list_item
    shopping_list_id: UUID4
    shopping_list_item_id: UUID4


class EventShoppingListItemBulkData(EventDocumentDataBase):
    document_type = EventDocumentType.shopping_list_item
    shopping_list_id: UUID4
    shopping_list_item_ids: list[UUID4]


class EventRecipeData(EventDocumentDataBase):
    document_type = EventDocumentType.recipe
    recipe_slug: str


class EventRecipeBulkReportData(EventDocumentDataBase):
    document_type = EventDocumentType.recipe_bulk_report
    report_id: UUID4


class EventRecipeTimelineEventData(EventDocumentDataBase):
    document_type = EventDocumentType.recipe_timeline_event
    recipe_slug: str
    recipe_timeline_event_id: UUID4


class EventTagData(EventDocumentDataBase):
    document_type = EventDocumentType.tag
    tag_id: UUID4


class EventWebhookData(EventDocumentDataBase):
    webhook_start_dt: datetime
    webhook_end_dt: datetime
    webhook_body: Any


class EventBusMessage(MealieModel):
    title: str
    body: str = ""

    @classmethod
    def from_type(cls, event_type: EventTypes, body: str = "") -> "EventBusMessage":
        title = event_type.name.replace("_", " ").title()
        return cls(title=title, body=body)


class Event(MealieModel):
    message: EventBusMessage
    event_type: EventTypes
    integration_id: str
    document_data: EventDocumentDataBase

    # set at instantiation
    event_id: UUID4 | None
    timestamp: datetime | None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.event_id = uuid.uuid4()
        self.timestamp = datetime.now()
