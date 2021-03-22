import json

import pytest
from tests.test_routes.utils.routes_data import recipe_test_data
from tests.utils.routes import MEALPLAN_ALL, MEALPLAN_CREATE, MEALPLAN_PREFIX, RECIPES_CREATE_URL, RECIPES_PREFIX


def get_meal_plan_template(first=None, second=None):
    return {
        "group": "Home",
        "startDate": "2021-01-18",
        "endDate": "2021-01-19",
        "meals": [
            {
                "slug": first,
                "date": "2021-1-17",
            },
            {
                "slug": second,
                "date": "2021-1-18",
            },
        ],
    }


## Meal Routes


@pytest.fixture
def slug_1(api_client):
    # Slug 1

    slug_1 = api_client.post(RECIPES_CREATE_URL, json={"url": recipe_test_data[0].url})
    slug_1 = json.loads(slug_1.content)

    yield slug_1

    api_client.delete(RECIPES_PREFIX + "/" + slug_1)


@pytest.fixture
def slug_2(api_client):
    # Slug 2
    slug_2 = api_client.post(RECIPES_CREATE_URL, json={"url": recipe_test_data[1].url})
    slug_2 = json.loads(slug_2.content)

    yield slug_2

    api_client.delete(RECIPES_PREFIX + "/" + slug_2)


def test_create_mealplan(api_client, slug_1, slug_2, token):
    meal_plan = get_meal_plan_template()
    meal_plan["meals"][0]["slug"] = slug_1
    meal_plan["meals"][1]["slug"] = slug_2

    response = api_client.post(MEALPLAN_CREATE, json=meal_plan, headers=token)
    assert response.status_code == 200


def test_read_mealplan(api_client, slug_1, slug_2, token):
    response = api_client.get(MEALPLAN_ALL, headers=token)

    assert response.status_code == 200

    meal_plan = get_meal_plan_template(slug_1, slug_2)

    new_meal_plan = json.loads(response.text)
    meals = new_meal_plan[0]["meals"]

    assert meals[0]["slug"] == meal_plan["meals"][0]["slug"]
    assert meals[1]["slug"] == meal_plan["meals"][1]["slug"]


def test_update_mealplan(api_client, slug_1, slug_2, token):

    response = api_client.get(MEALPLAN_ALL, headers=token)

    existing_mealplan = json.loads(response.text)
    existing_mealplan = existing_mealplan[0]

    ## Swap
    plan_uid = existing_mealplan.get("uid")
    existing_mealplan["meals"][0]["slug"] = slug_2
    existing_mealplan["meals"][1]["slug"] = slug_1

    response = api_client.put(f"{MEALPLAN_PREFIX}/{plan_uid}", json=existing_mealplan, headers=token)

    assert response.status_code == 200

    response = api_client.get(MEALPLAN_ALL, headers=token)
    existing_mealplan = json.loads(response.text)
    existing_mealplan = existing_mealplan[0]

    assert existing_mealplan["meals"][0]["slug"] == slug_2
    assert existing_mealplan["meals"][1]["slug"] == slug_1


def test_delete_mealplan(api_client, token):
    response = api_client.get(MEALPLAN_ALL, headers=token)

    assert response.status_code == 200
    existing_mealplan = json.loads(response.text)
    existing_mealplan = existing_mealplan[0]

    plan_uid = existing_mealplan.get("uid")
    response = api_client.delete(f"{MEALPLAN_PREFIX}/{plan_uid}")

    assert response.status_code == 200
