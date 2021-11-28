from uuid import uuid4

from mealie.db.data_access_layer.access_model_factory import Database
from mealie.schema.group.group_preferences import CreateGroupPreferences
from mealie.schema.user.user import GroupBase, GroupInDB


def create_new_group(db: Database, g_base: GroupBase, g_preferences: CreateGroupPreferences = None) -> GroupInDB:
    created_group = db.groups.create(g_base)

    # Assign Temporary ID before group is created
    g_preferences = g_preferences or CreateGroupPreferences(group_id=uuid4())

    g_preferences.group_id = created_group.id

    db.group_preferences.create(g_preferences)

    return created_group
