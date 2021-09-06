from mealie.db.database import get_database
from mealie.schema.group.group_preferences import CreateGroupPreferences
from mealie.schema.user.user import GroupBase, GroupInDB


def create_new_group(session, g_base: GroupBase, g_preferences: CreateGroupPreferences = None) -> GroupInDB:
    db = get_database()
    created_group = db.groups.create(session, g_base)

    g_preferences = g_preferences or CreateGroupPreferences(group_id=0)

    g_preferences.group_id = created_group.id

    db.group_preferences.create(session, g_preferences)

    return created_group
