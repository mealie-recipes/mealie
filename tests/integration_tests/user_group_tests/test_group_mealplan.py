from datetime import date, timedelta

from fastapi.testclient import TestClient

from mealie.schema.meal_plan.new_meal import CreatePlanEntry
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser
import random


def route_all_slice(page: int, perPage: int, start_date: str, end_date: str):
    return f"{api_routes.groups_mealplans}?page={page}&perPage={perPage}&start_date={start_date}&end_date={end_date}"


def test_create_mealplan_no_recipe(api_client: TestClient, unique_user: TestUser):
    title = random_string(length=25)
    text = random_string(length=25)
    new_plan = CreatePlanEntry(date=date.today(), entry_type="breakfast", title=title, text=text).dict()
    new_plan["date"] = date.today().strftime("%Y-%m-%d")

    response = api_client.post(api_routes.groups_mealplans, json=new_plan, headers=unique_user.token)

    assert response.status_code == 201

    response_json = response.json()
    assert response_json["title"] == title
    assert response_json["text"] == text


def test_create_mealplan_with_recipe(api_client: TestClient, unique_user: TestUser):
    recipe_name = random_string(length=25)
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=unique_user.token)
    assert response.status_code == 201

    response = api_client.get(api_routes.recipes_slug(recipe_name), headers=unique_user.token)
    recipe = response.json()
    recipe_id = recipe["id"]

    new_plan = CreatePlanEntry(date=date.today(), entry_type="dinner", recipe_id=recipe_id).dict(by_alias=True)
    new_plan["date"] = date.today().strftime("%Y-%m-%d")
    new_plan["recipeId"] = str(recipe_id)

    response = api_client.post(api_routes.groups_mealplans, json=new_plan, headers=unique_user.token)
    response_json = response.json()
    assert response.status_code == 201

    assert response_json["recipe"]["slug"] == recipe_name


def test_crud_mealplan(api_client: TestClient, unique_user: TestUser):
    new_plan = CreatePlanEntry(
        date=date.today(), entry_type="breakfast", title=random_string(), text=random_string(), quantity=2.5
    ).dict()

    # Create
    new_plan["date"] = date.today().strftime("%Y-%m-%d")
    response = api_client.post(api_routes.groups_mealplans, json=new_plan, headers=unique_user.token)
    response_json = response.json()
    assert response.status_code == 201
    plan_id = response_json["id"]

    # Update
    response_json["title"] = random_string()
    response_json["text"] = random_string()
    response_json["quantity"] = random.uniform(1.0, 5.0)

    response = api_client.put(
        api_routes.groups_mealplans_item_id(plan_id), headers=unique_user.token, json=response_json
    )

    assert response.status_code == 200

    assert response.json()["title"] == response_json["title"]
    assert response.json()["text"] == response_json["text"]
    assert response.json()["quantity"] == response_json["quantity"]

    # Delete
    response = api_client.delete(api_routes.groups_mealplans_item_id(plan_id), headers=unique_user.token)

    assert response.status_code == 200

    response = api_client.get(api_routes.groups_mealplans_item_id(plan_id), headers=unique_user.token)
    assert response.status_code == 404


def test_get_all_mealplans(api_client: TestClient, unique_user: TestUser):
    for _ in range(3):
        new_plan = CreatePlanEntry(
            date=date.today(),
            entry_type="breakfast",
            title=random_string(),
            text=random_string(),
        ).dict()

        new_plan["date"] = date.today().strftime("%Y-%m-%d")
        response = api_client.post(api_routes.groups_mealplans, json=new_plan, headers=unique_user.token)
        assert response.status_code == 201

    response = api_client.get(api_routes.groups_mealplans, headers=unique_user.token, params={"page": 1, "perPage": -1})

    assert response.status_code == 200
    assert len(response.json()["items"]) >= 3


def test_get_slice_mealplans(api_client: TestClient, unique_user: TestUser):
    # Make List of 10 dates from now to +10 days
    dates = [date.today() + timedelta(days=x) for x in range(10)]

    # Make a list of 10 meal plans
    meal_plans = [
        CreatePlanEntry(date=date, entry_type="breakfast", title=random_string(), text=random_string()).dict()
        for date in dates
    ]

    # Add the meal plans to the database
    for meal_plan in meal_plans:
        meal_plan["date"] = meal_plan["date"].strftime("%Y-%m-%d")
        response = api_client.post(api_routes.groups_mealplans, json=meal_plan, headers=unique_user.token)
        assert response.status_code == 201

    # Get meal slice of meal plans from database
    slices = [dates, dates[1:2], dates[2:3], dates[3:4], dates[4:5]]

    for date_range in slices:
        start_date = date_range[0].strftime("%Y-%m-%d")
        end_date = date_range[-1].strftime("%Y-%m-%d")

        response = api_client.get(route_all_slice(1, -1, start_date, end_date), headers=unique_user.token)

        assert response.status_code == 200
        response_json = response.json()

        for meal_plan in response_json["items"]:
            assert meal_plan["date"] in [date.strftime("%Y-%m-%d") for date in date_range]


def test_get_mealplan_today(api_client: TestClient, unique_user: TestUser):
    # Create Meal Plans for today
    test_meal_plans = [
        CreatePlanEntry(date=date.today(), entry_type="breakfast", title=random_string(), text=random_string()).dict()
        for _ in range(3)
    ]

    # Add the meal plans to the database
    for meal_plan in test_meal_plans:
        meal_plan["date"] = meal_plan["date"].strftime("%Y-%m-%d")
        response = api_client.post(api_routes.groups_mealplans, json=meal_plan, headers=unique_user.token)
        assert response.status_code == 201

    # Get meal plan for today
    response = api_client.get(api_routes.groups_mealplans_today, headers=unique_user.token)

    assert response.status_code == 200

    response_json = response.json()

    for meal_plan in response_json:
        assert meal_plan["date"] == date.today().strftime("%Y-%m-%d")
