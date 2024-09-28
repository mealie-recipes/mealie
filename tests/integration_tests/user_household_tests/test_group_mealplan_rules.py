from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from mealie.schema.meal_plan.plan_rules import PlanRulesOut
from mealie.schema.recipe.recipe import RecipeCategory
from mealie.schema.recipe.recipe_category import CategorySave
from tests import utils
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


@pytest.fixture(scope="function")
def category(unique_user: TestUser):
    database = unique_user.repos
    slug = utils.random_string(length=10)
    model = database.categories.create(CategorySave(group_id=unique_user.group_id, slug=slug, name=slug))

    yield model

    try:
        database.categories.delete(model.slug)
    except Exception:
        pass


@pytest.fixture(scope="function")
def plan_rule(api_client: TestClient, unique_user: TestUser):
    payload = {
        "groupId": unique_user.group_id,
        "householdId": unique_user.household_id,
        "day": "monday",
        "entryType": "breakfast",
        "categories": [],
    }

    response = api_client.post(
        api_routes.households_mealplans_rules, json=utils.jsonify(payload), headers=unique_user.token
    )
    assert response.status_code == 201
    plan_rule = PlanRulesOut.model_validate(response.json())
    yield plan_rule

    # cleanup
    api_client.delete(api_routes.households_mealplans_rules_item_id(plan_rule.id), headers=unique_user.token)


def test_group_mealplan_rules_create(api_client: TestClient, unique_user: TestUser, category: RecipeCategory):
    database = unique_user.repos
    payload = {
        "groupId": unique_user.group_id,
        "householdId": unique_user.household_id,
        "day": "monday",
        "entryType": "breakfast",
        "categories": [category.model_dump()],
    }

    response = api_client.post(
        api_routes.households_mealplans_rules, json=utils.jsonify(payload), headers=unique_user.token
    )
    assert response.status_code == 201

    # Validate the response data
    response_data = response.json()
    assert response_data["groupId"] == str(unique_user.group_id)
    assert response_data["householdId"] == str(unique_user.household_id)
    assert response_data["day"] == "monday"
    assert response_data["entryType"] == "breakfast"
    assert len(response_data["categories"]) == 1
    assert response_data["categories"][0]["slug"] == category.slug

    # Validate database entry
    rule = database.group_meal_plan_rules.get_one(UUID(response_data["id"]))
    assert rule

    assert str(rule.group_id) == unique_user.group_id
    assert str(rule.household_id) == unique_user.household_id
    assert rule.day == "monday"
    assert rule.entry_type == "breakfast"
    assert len(rule.categories) == 1
    assert rule.categories[0].slug == category.slug

    # Cleanup
    database.group_meal_plan_rules.delete(rule.id)


def test_group_mealplan_rules_read(api_client: TestClient, unique_user: TestUser, plan_rule: PlanRulesOut):
    response = api_client.get(api_routes.households_mealplans_rules_item_id(plan_rule.id), headers=unique_user.token)
    assert response.status_code == 200

    # Validate the response data
    response_data = response.json()
    assert response_data["id"] == str(plan_rule.id)
    assert response_data["groupId"] == str(unique_user.group_id)
    assert response_data["householdId"] == str(unique_user.household_id)
    assert response_data["day"] == "monday"
    assert response_data["entryType"] == "breakfast"
    assert len(response_data["categories"]) == 0


def test_group_mealplan_rules_update(api_client: TestClient, unique_user: TestUser, plan_rule: PlanRulesOut):
    payload = {
        "groupId": unique_user.group_id,
        "householdId": unique_user.household_id,
        "day": "tuesday",
        "entryType": "lunch",
    }

    response = api_client.put(
        api_routes.households_mealplans_rules_item_id(plan_rule.id), json=payload, headers=unique_user.token
    )
    assert response.status_code == 200

    # Validate the response data
    response_data = response.json()
    assert response_data["id"] == str(plan_rule.id)
    assert response_data["groupId"] == str(unique_user.group_id)
    assert response_data["householdId"] == str(unique_user.household_id)
    assert response_data["day"] == "tuesday"
    assert response_data["entryType"] == "lunch"
    assert len(response_data["categories"]) == 0


def test_group_mealplan_rules_delete(api_client: TestClient, unique_user: TestUser, plan_rule: PlanRulesOut):
    response = api_client.get(api_routes.households_mealplans_rules_item_id(plan_rule.id), headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.delete(api_routes.households_mealplans_rules_item_id(plan_rule.id), headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.get(api_routes.households_mealplans_rules_item_id(plan_rule.id), headers=unique_user.token)
    assert response.status_code == 404
