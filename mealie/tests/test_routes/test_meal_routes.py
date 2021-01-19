import json

from tests.test_routes.utils.routes_data import recipe_test_data


def cleanup(api_client):
    api_client.delete(f"/api/recipe/{recipe_test_data[0].expected_slug}/delete/")
    api_client.delete(f"/api/recipe/{recipe_test_data[1].expected_slug}/delete/")


def get_meal_plan_template(first=None, second=None):
    return {
        "startDate": "2021-01-18",
        "endDate": "2021-01-19",
        "meals": [
            {
                "slug": first,
                "date": "2021-1-17",
                "dateText": "Monday, January 18, 2021",
            },
            {
                "slug": second,
                "date": "2021-1-18",
                "dateText": "Tueday, January 19, 2021",
            },
        ],
    }


slug_1 = None
slug_2 = None


def get_slugs(api_client):
    # Slug 1
    global slug_1
    global slug_2
    if slug_1 == None:
        slug_1 = api_client.post(
            "/api/recipe/create-url/", json={"url": recipe_test_data[0].url}
        )
        slug_1 = json.loads(slug_1.content)

        # Slug 2
        slug_2 = api_client.post(
            "/api/recipe/create-url/", json={"url": recipe_test_data[1].url}
        )
        slug_2 = json.loads(slug_2.content)

    return slug_1, slug_2


def test_create_mealplan(api_client):
    slug_1, slug_2 = get_slugs(api_client)
    meal_plan = get_meal_plan_template()
    meal_plan["meals"][0]["slug"] = slug_1
    meal_plan["meals"][1]["slug"] = slug_2

    response = api_client.post("/api/meal-plan/create/", json=meal_plan)
    assert response.status_code == 200


def test_read_mealplan(api_client):
    response = api_client.get("/api/meal-plan/all/")

    assert response.status_code == 200

    slug_1, slug_2 = get_slugs(api_client)
    meal_plan = get_meal_plan_template(slug_1, slug_2)

    new_meal_plan = json.loads(response.text)
    meals = new_meal_plan[0]["meals"]

    assert meals[0]["slug"] == meal_plan["meals"][0]["slug"]
    assert meals[1]["slug"] == meal_plan["meals"][1]["slug"]


def test_update_mealplan(api_client):
    slug_1, slug_2 = get_slugs(api_client)

    response = api_client.get("/api/meal-plan/all/")

    existing_mealplan = json.loads(response.text)
    existing_mealplan = existing_mealplan[0]

    ## Swap
    plan_uid = existing_mealplan.get("uid")
    existing_mealplan["meals"][0]["slug"] = slug_2
    existing_mealplan["meals"][1]["slug"] = slug_1

    response = api_client.post(
        f"/api/meal-plan/{plan_uid}/update/", json=existing_mealplan
    )

    assert response.status_code == 200

    response = api_client.get("/api/meal-plan/all/")
    existing_mealplan = json.loads(response.text)
    existing_mealplan = existing_mealplan[0]

    assert existing_mealplan["meals"][0]["slug"] == slug_2
    assert existing_mealplan["meals"][1]["slug"] == slug_1


def test_delete_mealplan(api_client):
    response = api_client.get("/api/meal-plan/all/")
    existing_mealplan = json.loads(response.text)
    existing_mealplan = existing_mealplan[0]

    plan_uid = existing_mealplan.get("uid")
    response = api_client.delete(f"/api/meal-plan/{plan_uid}/delete/")

    assert response.status_code == 200
