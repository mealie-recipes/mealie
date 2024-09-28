from pydantic import UUID4, ConfigDict
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.household import GroupEventNotifierModel
from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase

# =============================================================================
# Group Events Notifier Options


class GroupEventNotifierOptions(MealieModel):
    """
    These events are in-sync with the EventTypes found in the EventBusService.
    If you modify this, make sure to update the EventBusService as well.
    """

    test_message: bool = False
    webhook_task: bool = False

    recipe_created: bool = False
    recipe_updated: bool = False
    recipe_deleted: bool = False

    user_signup: bool = False

    data_migrations: bool = False
    data_export: bool = False
    data_import: bool = False

    mealplan_entry_created: bool = False

    shopping_list_created: bool = False
    shopping_list_updated: bool = False
    shopping_list_deleted: bool = False

    cookbook_created: bool = False
    cookbook_updated: bool = False
    cookbook_deleted: bool = False

    tag_created: bool = False
    tag_updated: bool = False
    tag_deleted: bool = False

    category_created: bool = False
    category_updated: bool = False
    category_deleted: bool = False


class GroupEventNotifierOptionsSave(GroupEventNotifierOptions):
    notifier_id: UUID4


class GroupEventNotifierOptionsOut(GroupEventNotifierOptions):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)


# =======================================================================
# Notifiers


class GroupEventNotifierCreate(MealieModel):
    name: str
    apprise_url: str | None = None


class GroupEventNotifierSave(GroupEventNotifierCreate):
    enabled: bool = True
    group_id: UUID4
    household_id: UUID4
    options: GroupEventNotifierOptions = GroupEventNotifierOptions()


class GroupEventNotifierUpdate(GroupEventNotifierSave):
    id: UUID4
    apprise_url: str | None = None


class GroupEventNotifierOut(MealieModel):
    id: UUID4
    name: str
    enabled: bool
    group_id: UUID4
    household_id: UUID4
    options: GroupEventNotifierOptionsOut
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(GroupEventNotifierModel.options)]


class GroupEventPagination(PaginationBase):
    items: list[GroupEventNotifierOut]


class GroupEventNotifierPrivate(GroupEventNotifierOut):
    apprise_url: str
    model_config = ConfigDict(from_attributes=True)
