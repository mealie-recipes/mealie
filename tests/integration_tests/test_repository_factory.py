import inspect
import time
from functools import cached_property
from uuid import uuid4

import pytest
from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.repos._utils import NOT_SET, NotSet
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_generic import GroupRepositoryGeneric, HouseholdRepositoryGeneric, RepositoryGeneric
from mealie.schema._mealie.mealie_model import MealieModel
from mealie.schema.household.webhook import SaveWebhook
from mealie.schema.recipe.recipe_ingredient import SaveIngredientFood
from mealie.schema.response.pagination import PaginationQuery
from tests.utils.factories import random_string


@pytest.mark.parametrize("group_id", [uuid4(), None, NOT_SET])
@pytest.mark.parametrize("household_id", [uuid4(), None, NOT_SET])
def test_get_repositories_sets_ids(
    session: Session, group_id: UUID4 | None | NotSet, household_id: UUID4 | None | NotSet
):
    kwargs = {}
    if not isinstance(group_id, NotSet):
        kwargs["group_id"] = group_id
    if not isinstance(household_id, NotSet):
        kwargs["household_id"] = household_id

    repositories = get_repositories(session, **kwargs)
    assert repositories.group_id == group_id
    assert repositories.household_id == household_id

    # test that sentinel is used correctly
    if isinstance(group_id, NotSet):
        assert repositories.group_id is NOT_SET
    if isinstance(household_id, NotSet):
        assert repositories.household_id is NOT_SET


def test_repository_generic_constructor(session: Session):
    RepositoryGeneric(session, "id", MealieModel, SqlAlchemyBase)


def test_repository_group_constructor(session: Session):
    BASE_ARGS = (session, "id", MealieModel, SqlAlchemyBase)

    with pytest.raises(ValueError):
        GroupRepositoryGeneric(*BASE_ARGS, group_id=NOT_SET)

    GroupRepositoryGeneric(*BASE_ARGS, group_id=None)
    GroupRepositoryGeneric(*BASE_ARGS, group_id=uuid4())


def test_repository_household_constructor(session: Session):
    BASE_ARGS = (session, "id", MealieModel, SqlAlchemyBase)

    with pytest.raises(ValueError):
        HouseholdRepositoryGeneric(*BASE_ARGS, group_id=NOT_SET, household_id=NOT_SET)
        HouseholdRepositoryGeneric(*BASE_ARGS, group_id=uuid4(), household_id=NOT_SET)
        HouseholdRepositoryGeneric(*BASE_ARGS, group_id=NOT_SET, household_id=uuid4())

    HouseholdRepositoryGeneric(*BASE_ARGS, group_id=None, household_id=None)
    HouseholdRepositoryGeneric(*BASE_ARGS, group_id=uuid4(), household_id=None)
    HouseholdRepositoryGeneric(*BASE_ARGS, group_id=None, household_id=uuid4())
    HouseholdRepositoryGeneric(*BASE_ARGS, group_id=uuid4(), household_id=uuid4())


@pytest.mark.parametrize("use_group_id", [True, False])
@pytest.mark.parametrize("use_household_id", [True, False])
def test_all_repositories_constructors(session: Session, use_group_id: bool, use_household_id: bool):
    kwargs = {}
    if use_group_id:
        kwargs["group_id"] = uuid4()
    if use_household_id:
        kwargs["household_id"] = uuid4()
    repositories = get_repositories(session, **kwargs)
    for name, member in inspect.getmembers(repositories.__class__):
        if not isinstance(member, cached_property):
            continue
        signature = inspect.signature(member.func)
        repo_type = signature.return_annotation
        try:
            if not issubclass(repo_type, RepositoryGeneric):
                continue
        except TypeError:
            continue

        if issubclass(repo_type, HouseholdRepositoryGeneric):
            if not (use_group_id and use_household_id):
                with pytest.raises(ValueError):
                    getattr(repositories, name)
            else:
                repo = getattr(repositories, name)
                assert repo.group_id == kwargs["group_id"]
                assert repo.household_id == kwargs["household_id"]
        elif issubclass(repo_type, GroupRepositoryGeneric):
            if not use_group_id:
                with pytest.raises(ValueError):
                    getattr(repositories, name)
            else:
                repo = getattr(repositories, name)
                assert repo.group_id == kwargs["group_id"]
                assert repo.household_id is None
        else:
            repo = getattr(repositories, name)
            assert repo.group_id is None
            assert repo.household_id is None


def test_group_repositories_filter_by_group(session: Session):
    unfiltered_repos = get_repositories(session, group_id=None, household_id=None)
    group_1 = unfiltered_repos.groups.create({"name": random_string()})
    group_2 = unfiltered_repos.groups.create({"name": random_string()})

    group_1_repos = get_repositories(session, group_id=group_1.id, household_id=None)
    group_2_repos = get_repositories(session, group_id=group_2.id, household_id=None)
    food_1 = group_1_repos.ingredient_foods.create(
        SaveIngredientFood(id=uuid4(), group_id=group_1.id, name=random_string())
    )
    food_2 = group_2_repos.ingredient_foods.create(
        SaveIngredientFood(id=uuid4(), group_id=group_2.id, name=random_string())
    )

    # unfiltered_repos should find both foods
    assert food_1 == unfiltered_repos.ingredient_foods.get_one(food_1.id)
    assert food_2 == unfiltered_repos.ingredient_foods.get_one(food_2.id)
    assert sorted([food_1, food_2], key=lambda x: x.id) == sorted(
        unfiltered_repos.ingredient_foods.page_all(PaginationQuery(page=1, per_page=-1)).items, key=lambda x: x.id
    )

    # group_repos should only find foods with the correct group_id
    assert food_1 == group_1_repos.ingredient_foods.get_one(food_1.id)
    assert group_1_repos.ingredient_foods.get_one(food_2.id) is None
    assert [food_1] == group_1_repos.ingredient_foods.page_all(PaginationQuery(page=1, per_page=-1)).items

    assert group_2_repos.ingredient_foods.get_one(food_1.id) is None
    assert food_2 == group_2_repos.ingredient_foods.get_one(food_2.id)
    assert [food_2] == group_2_repos.ingredient_foods.page_all(PaginationQuery(page=1, per_page=-1)).items


def test_household_repositories_filter_by_household(session: Session):
    unfiltered_repos = get_repositories(session, group_id=None, household_id=None)
    group = unfiltered_repos.groups.create({"name": random_string()})
    group_repos = get_repositories(session, group_id=group.id, household_id=None)
    household_1 = group_repos.households.create({"name": random_string(), "group_id": group.id})
    household_2 = group_repos.households.create({"name": random_string(), "group_id": group.id})

    household_1_repos = get_repositories(session, group_id=group.id, household_id=household_1.id)
    household_2_repos = get_repositories(session, group_id=group.id, household_id=household_2.id)
    webhook_1 = household_1_repos.webhooks.create(
        SaveWebhook(group_id=group.id, household_id=household_1.id, scheduled_time=time.time())
    )
    webhook_2 = household_2_repos.webhooks.create(
        SaveWebhook(group_id=group.id, household_id=household_2.id, scheduled_time=time.time())
    )

    # unfiltered_repos and group_repos should find both webhooks
    for repos in [unfiltered_repos, group_repos]:
        assert webhook_1 == repos.webhooks.get_one(webhook_1.id)
        assert webhook_2 == repos.webhooks.get_one(webhook_2.id)
        assert sorted([webhook_1, webhook_2], key=lambda x: x.id) == sorted(
            repos.webhooks.page_all(PaginationQuery(page=1, per_page=-1)).items, key=lambda x: x.id
        )

    # household_repos should only find webhooks with the correct household_id
    assert webhook_1 == household_1_repos.webhooks.get_one(webhook_1.id)
    assert household_1_repos.webhooks.get_one(webhook_2.id) is None
    assert [webhook_1] == household_1_repos.webhooks.page_all(PaginationQuery(page=1, per_page=-1)).items

    assert household_2_repos.webhooks.get_one(webhook_1.id) is None
    assert webhook_2 == household_2_repos.webhooks.get_one(webhook_2.id)
    assert [webhook_2] == household_2_repos.webhooks.page_all(PaginationQuery(page=1, per_page=-1)).items

    # a different group's repos shouldn't find anything
    other_group = unfiltered_repos.groups.create({"name": random_string()})
    for household_id in [household_1.id, household_2.id]:
        other_group_repos = get_repositories(session, group_id=other_group.id, household_id=household_id)
        assert other_group_repos.webhooks.get_one(webhook_1.id) is None
        assert other_group_repos.webhooks.get_one(webhook_2.id) is None
        assert other_group_repos.webhooks.page_all(PaginationQuery(page=1, per_page=-1)).items == []
