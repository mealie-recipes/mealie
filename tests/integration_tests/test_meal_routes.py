import json

import pytest
from fastapi.testclient import TestClient
from tests.app_routes import AppRoutes
from tests.utils.recipe_data import RecipeSiteTestCase


def get_meal_plan_template(first=None, second=None):
    return {
        "group": "Home",
        "startDate": "2021-01-18",
        "endDate": "2021-01-19",
        "planDays": [
            {
                "date": "2021-1-18",
                "meals": [{"slug": first, "name": "", "description": ""}],
            },
            {
                "date": "2021-1-19",
                "meals": [{"slug": second, "name": "", "description": ""}],
            },
        ],
    }


@pytest.fixture(scope="session")
def slug_1(api_client: TestClient, api_routes: AppRoutes, admin_token, recipe_store: list[RecipeSiteTestCase]):
    slug_1 = api_client.post(api_routes.recipes_create_url, json={"url": recipe_store[0].url}, headers=admin_token)
    slug_1 = json.loads(slug_1.content)

    yield slug_1

    api_client.delete(api_routes.recipes_recipe_slug(slug_1))


@pytest.fixture(scope="session")
def slug_2(api_client: TestClient, api_routes: AppRoutes, admin_token, recipe_store: list[RecipeSiteTestCase]):
    slug_2 = api_client.post(api_routes.recipes_create_url, json={"url": recipe_store[1].url}, headers=admin_token)
    slug_2 = json.loads(slug_2.content)

    yield slug_2

    api_client.delete(api_routes.recipes_recipe_slug(slug_2))


def test_create_mealplan(api_client: TestClient, api_routes: AppRoutes, slug_1, slug_2, admin_token):
    meal_plan = get_meal_plan_template(slug_1, slug_2)

    response = api_client.post(api_routes.meal_plans_create, json=meal_plan, headers=admin_token)
    assert response.status_code == 201


def test_read_mealplan(api_client: TestClient, api_routes: AppRoutes, slug_1, slug_2, admin_token):
    response = api_client.get(api_routes.meal_plans_all, headers=admin_token)

    assert response.status_code == 200

    meal_plan_template = get_meal_plan_template(slug_1, slug_2)

    created_meal_plan = json.loads(response.text)
    meals = created_meal_plan[0]["planDays"]

    assert meals[0]["meals"][0]["slug"] == meal_plan_template["planDays"][0]["meals"][0]["slug"]
    assert meals[1]["meals"][0]["slug"] == meal_plan_template["planDays"][1]["meals"][0]["slug"]


def test_update_mealplan(api_client: TestClient, api_routes: AppRoutes, slug_1, slug_2, admin_token):

    response = api_client.get(api_routes.meal_plans_all, headers=admin_token)

    existing_mealplan = json.loads(response.text)
    existing_mealplan = existing_mealplan[0]

    # Swap
    plan_uid = existing_mealplan.get("uid")
    existing_mealplan["planDays"][0]["meals"][0]["slug"] = slug_2
    existing_mealplan["planDays"][1]["meals"][0]["slug"] = slug_1

    response = api_client.put(api_routes.meal_plans_plan_id(plan_uid), json=existing_mealplan, headers=admin_token)

    assert response.status_code == 200

    response = api_client.get(api_routes.meal_plans_all, headers=admin_token)
    existing_mealplan = json.loads(response.text)
    existing_mealplan = existing_mealplan[0]

    assert existing_mealplan["planDays"][0]["meals"][0]["slug"] == slug_2
    assert existing_mealplan["planDays"][1]["meals"][0]["slug"] == slug_1


def test_delete_mealplan(api_client: TestClient, api_routes: AppRoutes, admin_token):
    response = api_client.get(api_routes.meal_plans_all, headers=admin_token)

    assert response.status_code == 200
    existing_mealplan = json.loads(response.text)
    existing_mealplan = existing_mealplan[0]

    plan_uid = existing_mealplan.get("uid")
    response = api_client.delete(api_routes.meal_plans_plan_id(plan_uid), headers=admin_token)

    assert response.status_code == 200
