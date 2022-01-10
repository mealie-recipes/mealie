from enum import Enum, auto


class EventTypes(Enum):
    test_message = auto()

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


class EventBusMessage:
    title: str
    body: str = ""

    def __init__(self, title, body) -> None:
        self.title = title
        self.body = body

    @classmethod
    def from_type(cls, event_type: EventTypes, body: str = "") -> "EventBusMessage":
        title = event_type.name.replace("_", " ").title()
        return cls(title=title, body=body)
