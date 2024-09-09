from uuid import UUID

import pytest
from slugify import slugify

from mealie.schema.cookbook.cookbook import SaveCookBook
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def cookbook_data(user: TestUser, **kwargs):
    data = {
        "name": random_string(),
        "group_id": UUID(user.group_id),
        "household_id": UUID(user.household_id),
    } | kwargs

    return SaveCookBook(**data)


@pytest.mark.parametrize("use_create_many", [True, False])
def test_create_cookbook_ignores_slug(unique_user: TestUser, use_create_many: bool):
    bad_slug = random_string()
    cb_data = cookbook_data(unique_user, slug=bad_slug)
    if use_create_many:
        result = unique_user.repos.cookbooks.create_many([cb_data])
        assert len(result) == 1
        cb = result[0]
    else:
        cb = unique_user.repos.cookbooks.create(cb_data)
    assert cb.slug == slugify(cb.name) != bad_slug


@pytest.mark.parametrize("use_create_many", [True, False])
def test_create_cookbook_duplicate_name(unique_user: TestUser, use_create_many: bool):
    cb_1_data = cookbook_data(unique_user)
    cb_2_data = cookbook_data(unique_user, name=cb_1_data.name)

    cb_1 = unique_user.repos.cookbooks.create(cb_1_data)
    unique_user.repos.session.commit()

    if use_create_many:
        result = unique_user.repos.cookbooks.create_many([cb_2_data])
        assert len(result) == 1
        cb_2 = result[0]
    else:
        cb_2 = unique_user.repos.cookbooks.create(cb_2_data)

    assert cb_1.id != cb_2.id
    assert cb_1.group_id == cb_2.group_id
    assert cb_1.household_id != cb_2.household_id
    assert cb_1.name == cb_2.name
    assert cb_1.slug != cb_2.slug
