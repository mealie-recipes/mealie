import pytest
from slugify import slugify

from mealie.schema.recipe.recipe_category import CategorySave, TagSave
from mealie.schema.recipe.recipe_tool import RecipeToolSave
from mealie.services.recipe.organizer_resolver import OrganizerResolver
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


@pytest.fixture()
def resolver(unique_user: TestUser) -> OrganizerResolver:
    return OrganizerResolver(unique_user.repos)


def test_matches_an_existing_tag_exactly(unique_user: TestUser, resolver: OrganizerResolver):
    name = random_string()
    existing = unique_user.repos.tags.create(TagSave(name=name, group_id=unique_user.repos.group_id))

    resolved = resolver.resolve_tags([name], create_missing=False)
    assert [tag.id for tag in resolved] == [existing.id]


def test_matches_an_existing_tag_regardless_of_case_and_spacing(unique_user: TestUser, resolver: OrganizerResolver):
    existing = unique_user.repos.tags.create(TagSave(name="Slow Cooker", group_id=unique_user.repos.group_id))

    resolved = resolver.resolve_tags(["slow   cooker"], create_missing=False)
    assert [tag.id for tag in resolved] == [existing.id]


def test_matches_a_close_variant(unique_user: TestUser, resolver: OrganizerResolver):
    existing = unique_user.repos.categories.create(CategorySave(name="Dinners", group_id=unique_user.repos.group_id))

    resolved = resolver.resolve_categories(["Dinner"], create_missing=False)
    assert [category.id for category in resolved] == [existing.id]


def test_does_not_match_below_the_threshold(unique_user: TestUser, resolver: OrganizerResolver):
    unique_user.repos.tags.create(TagSave(name="Vegetarian", group_id=unique_user.repos.group_id))

    resolved = resolver.resolve_tags(["Vegan"], create_missing=False)
    assert resolved == []


def test_unmatched_names_are_dropped_when_not_creating(unique_user: TestUser, resolver: OrganizerResolver):
    resolved = resolver.resolve_tags([random_string(), random_string()], create_missing=False)
    assert resolved == []


def test_unmatched_names_are_created_when_requested(unique_user: TestUser, resolver: OrganizerResolver):
    name = random_string()

    resolved = resolver.resolve_tags([name], create_missing=True)
    assert [tag.name for tag in resolved] == [name]
    assert unique_user.repos.tags.get_one(slugify(name), "slug")


def test_existing_tools_are_reused_rather_than_recreated(unique_user: TestUser, resolver: OrganizerResolver):
    name = random_string()
    existing = unique_user.repos.tools.create(RecipeToolSave(name=name, group_id=unique_user.repos.group_id))

    resolved = resolver.resolve_tools([name], create_missing=True)
    assert [tool.id for tool in resolved] == [existing.id]


def test_duplicate_and_blank_names_are_collapsed(unique_user: TestUser, resolver: OrganizerResolver):
    name = random_string()

    resolved = resolver.resolve_tags([name, name.upper(), "  ", ""], create_missing=True)
    assert len(resolved) == 1


def test_existing_names_are_reported_for_prompt_injection(unique_user: TestUser, resolver: OrganizerResolver):
    tag = random_string()
    category = random_string()
    tool = random_string()

    unique_user.repos.tags.create(TagSave(name=tag, group_id=unique_user.repos.group_id))
    unique_user.repos.categories.create(CategorySave(name=category, group_id=unique_user.repos.group_id))
    unique_user.repos.tools.create(RecipeToolSave(name=tool, group_id=unique_user.repos.group_id))

    existing = resolver.existing_names()
    assert tag in existing["tags"]
    assert category in existing["categories"]
    assert tool in existing["tools"]
