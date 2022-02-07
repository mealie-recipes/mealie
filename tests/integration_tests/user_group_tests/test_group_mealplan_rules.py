from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import UUID4

from mealie.repos.all_repositories import AllRepositories
from mealie.schema.meal_plan.plan_rules import PlanRulesOut, PlanRulesSave
from mealie.schema.recipe.recipe import RecipeCategory
from tests import utils
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/groups/mealplans/rules"

    @staticmethod
    def item(item_id: UUID4) -> str:
        return f"{Routes.base}/{item_id}"


@pytest.fixture(scope="function")
def category(database: AllRepositories):
    slug = utils.random_string(length=10)
    model = database.categories.create(RecipeCategory(slug=slug, name=slug))

    yield model

    try:
        database.categories.delete(model.slug)
    except Exception:
        pass


@pytest.fixture(scope="function")
def plan_rule(database: AllRepositories, unique_user: TestUser):
    schema = PlanRulesSave(
        group_id=unique_user.group_id,
        day="monday",
        entry_type="breakfast",
        categories=[],
    )

    model = database.group_meal_plan_rules.create(schema)

    yield model

    try:
        database.group_meal_plan_rules.delete(model.id)
    except Exception:
        pass


def test_group_mealplan_rules_create(
    api_client: TestClient, unique_user: TestUser, category: RecipeCategory, database: AllRepositories
):
    payload = {
        "groupId": unique_user.group_id,
        "day": "monday",
        "entryType": "breakfast",
        "categories": [category.dict()],
    }

    response = api_client.post(Routes.base, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    # Validate the response data
    response_data = response.json()
    assert response_data["groupId"] == str(unique_user.group_id)
    assert response_data["day"] == "monday"
    assert response_data["entryType"] == "breakfast"
    assert len(response_data["categories"]) == 1
    assert response_data["categories"][0]["slug"] == category.slug

    # Validate database entry
    rule = database.group_meal_plan_rules.get_one(UUID(response_data["id"]))

    assert str(rule.group_id) == unique_user.group_id
    assert rule.day == "monday"
    assert rule.entry_type == "breakfast"
    assert len(rule.categories) == 1
    assert rule.categories[0].slug == category.slug

    # Cleanup
    database.group_meal_plan_rules.delete(rule.id)


def test_group_mealplan_rules_read(api_client: TestClient, unique_user: TestUser, plan_rule: PlanRulesOut):
    response = api_client.get(Routes.item(plan_rule.id), headers=unique_user.token)
    assert response.status_code == 200

    # Validate the response data
    response_data = response.json()
    assert response_data["id"] == str(plan_rule.id)
    assert response_data["groupId"] == str(unique_user.group_id)
    assert response_data["day"] == "monday"
    assert response_data["entryType"] == "breakfast"
    assert len(response_data["categories"]) == 0


def test_group_mealplan_rules_update(api_client: TestClient, unique_user: TestUser, plan_rule: PlanRulesOut):
    payload = {
        "groupId": unique_user.group_id,
        "day": "tuesday",
        "entryType": "lunch",
    }

    response = api_client.put(Routes.item(plan_rule.id), json=payload, headers=unique_user.token)
    assert response.status_code == 200

    # Validate the response data
    response_data = response.json()
    assert response_data["id"] == str(plan_rule.id)
    assert response_data["groupId"] == str(unique_user.group_id)
    assert response_data["day"] == "tuesday"
    assert response_data["entryType"] == "lunch"
    assert len(response_data["categories"]) == 0


def test_group_mealplan_rules_delete(
    api_client: TestClient, unique_user: TestUser, plan_rule: PlanRulesOut, database: AllRepositories
):
    response = api_client.delete(Routes.item(plan_rule.id), headers=unique_user.token)
    assert response.status_code == 200

    # Validate no entry in database
    assert database.group_meal_plan_rules.get_one(plan_rule.id) is None
