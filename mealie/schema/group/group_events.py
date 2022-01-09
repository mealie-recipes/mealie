from fastapi_camelcase import CamelModel
from pydantic import UUID4

# =============================================================================
# Group Events Notifier Options


class GroupEventNotifierOptions(CamelModel):
    recipe_create: bool = False
    recipe_update: bool = False
    recipe_delete: bool = False

    user_signup: bool = False

    data_migrations: bool = False
    data_export: bool = False
    data_import: bool = False

    new_mealplan_entry: bool = False

    shopping_list_create: bool = False
    shopping_list_update: bool = False
    shopping_list_delete: bool = False

    cookbook_create: bool = False
    cookbook_update: bool = False
    cookbook_delete: bool = False

    tag_create: bool = False
    tag_update: bool = False
    tag_delete: bool = False

    category_create: bool = False
    category_update: bool = False
    category_delete: bool = False


class GroupEventNotifierOptionsSave(GroupEventNotifierOptions):
    notifier_id: UUID4


class GroupEventNotifierOptionsOut(GroupEventNotifierOptions):
    id: UUID4

    class Config:
        orm_mode = True


# =======================================================================
# Notifiers


class GroupEventNotifierCreate(CamelModel):
    name: str
    apprise_url: str


class GroupEventNotifierSave(GroupEventNotifierCreate):
    enabled: bool = True
    group_id: UUID4
    options: GroupEventNotifierOptions = GroupEventNotifierOptions()


class GroupEventNotifierUpdate(GroupEventNotifierSave):
    id: UUID4
    apprise_url: str = None


class GroupEventNotifierOut(CamelModel):
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
