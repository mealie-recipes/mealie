from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.group_preferences import CreateGroupPreferences
from tests.utils.factories import random_int, random_string


def test_group_resolve_similar_names(database: AllRepositories):
    base_group_name = random_string()
    groups = database.groups.create_many({"name": base_group_name} for _ in range(random_int(3, 10)))

    seen_names = set()
    seen_slugs = set()
    for group in groups:
        assert group.name not in seen_names
        assert group.slug not in seen_slugs
        seen_names.add(group.name)
        seen_slugs.add(group.slug)

        assert base_group_name in group.name


def test_group_get_by_slug_or_id(database: AllRepositories):
    groups = [database.groups.create({"name": random_string()}) for _ in range(random_int(3, 10))]
    for group in groups:
        assert database.groups.get_by_slug_or_id(group.id) == group
        assert database.groups.get_by_slug_or_id(group.slug) == group


def test_group_get_all_public(database: AllRepositories):
    private_group = database.groups.create({"name": random_string()})
    prefs = database.group_preferences.create(CreateGroupPreferences(group_id=private_group.id))
    prefs.private_group = True
    prefs.recipe_public = True
    database.group_preferences.update(private_group.id, prefs)

    recipes_private = database.groups.create({"name": random_string()})
    prefs = database.group_preferences.create(CreateGroupPreferences(group_id=recipes_private.id))
    prefs.private_group = False
    prefs.recipe_public = False
    database.group_preferences.update(recipes_private.id, prefs)

    public_group = database.groups.create({"name": random_string()})
    prefs = database.group_preferences.create(CreateGroupPreferences(group_id=public_group.id))
    prefs.private_group = False
    prefs.recipe_public = True
    database.group_preferences.update(public_group.id, prefs)

    result = [g.id for g in database.groups.get_all_public()]
    assert public_group.id in result
    assert recipes_private.id not in result
    assert private_group.id not in result
