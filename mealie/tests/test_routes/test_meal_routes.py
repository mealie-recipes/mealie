import json

from tests.test_routes.utils.routes_data import recipe_test_data


def cleanup(api_client):
    api_client.delete(f"/api/recipe/{recipe_test_data[0].expected_slug}/delete/")
    api_client.delete(f"/api/recipe/{recipe_test_data[1].expected_slug}/delete/")


meal_plan = {
    "startDate": "2021-01-18",
    "endDate": "2021-01-19",
    "meals": [
        {
            "slug": None,
            "date": "2021-1-17",
            "dateText": "Monday, January 18, 2021",
        },
        {
            "slug": None,
            "date": "2021-1-18",
            "dateText": "Tueday, January 19, 2021",
        },
    ],
}


def test_create_mealplan(api_client):
    slug_1 = api_client.post(
        "/api/recipe/create-url/", json={"url": recipe_test_data[0].url}
    )
    slug_2 = api_client.post(
        "/api/recipe/create-url/", json={"url": recipe_test_data[1].url}
    )

    meal_plan["meals"][0]["slug"] = json.loads(slug_1.content)
    meal_plan["meals"][1]["slug"] = json.loads(slug_2.content)

    response = api_client.post("/api/meal-plan/create/", json=meal_plan)
    assert response.status_code == 200


def test_read_mealplan(api_client):
    response = api_client.get("/api/meal-plan/all/")

    assert response.status_code == 200

    new_meal_plan = json.loads(response.text)
    meals = new_meal_plan[0]["meals"]

    assert meals[0]["slug"] == meal_plan["meals"][0]["slug"]
    assert meals[1]["slug"] == meal_plan["meals"][1]["slug"]

    cleanup(api_client)


def test_update_mealplan(api_client):
    slug_1 = api_client.post(
        "/api/recipe/create-url/", json={"url": recipe_test_data[0].url}
    )
    slug_2 = api_client.post(
        "/api/recipe/create-url/", json={"url": recipe_test_data[1].url}
    )

    response = api_client.get("/api/meal-plan/all/")

    existing_mealplan = json.loads(response.text)
    existing_mealplan = existing_mealplan[0]

    ## Swap
    plan_uid = existing_mealplan.get("uid")
    existing_mealplan["meals"][0]["slug"] = json.loads(slug_2.content)
    existing_mealplan["meals"][1]["slug"] = json.loads(slug_1.content)

    response = api_client.post(
        f"/api/meal-plan/{plan_uid}/update/", json=existing_mealplan
    )

    assert response.status_code == 200

    response = api_client.get("/api/meal-plan/all/")
    existing_mealplan = json.loads(response.text)
    existing_mealplan = existing_mealplan[0]

    assert existing_mealplan["meals"][0]["slug"] == json.loads(slug_2.content)
    assert existing_mealplan["meals"][1]["slug"] == json.loads(slug_1.content)

    cleanup(api_client)


def test_delete_mealplan(api_client):
    response = api_client.get("/api/meal-plan/all/")
    existing_mealplan = json.loads(response.text)
    existing_mealplan = existing_mealplan[0]

    plan_uid = existing_mealplan.get("uid")
    response = api_client.delete(f"/api/meal-plan/{plan_uid}/delete/")

    assert response.status_code == 200
