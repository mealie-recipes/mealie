from pydantic import UUID4, NoneStr

from mealie.schema._mealie import MealieModel

# =============================================================================
# Group Events Notifier Options


class GroupEventNotifierOptions(MealieModel):
    """
    These events are in-sync with the EventTypes found in the EventBusService.
    If you modify this, make sure to update the EventBusService as well.
    """

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

    class Config:
        orm_mode = True


# =======================================================================
# Notifiers


class GroupEventNotifierCreate(MealieModel):
    name: str
    apprise_url: str


class GroupEventNotifierSave(GroupEventNotifierCreate):
    enabled: bool = True
    group_id: UUID4
    options: GroupEventNotifierOptions = GroupEventNotifierOptions()


class GroupEventNotifierUpdate(GroupEventNotifierSave):
    id: UUID4
    apprise_url: NoneStr = None


class GroupEventNotifierOut(MealieModel):
    id: UUID4
    name: str
    enabled: bool
    group_id: UUID4
    options: GroupEventNotifierOptionsOut

    class Config:
        orm_mode = True


class GroupEventNotifierPrivate(GroupEventNotifierOut):
    apprise_url: str

    class Config:
        orm_mode = True
