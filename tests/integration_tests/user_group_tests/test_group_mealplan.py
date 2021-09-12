from datetime import date

from fastapi.testclient import TestClient

from mealie.schema.meal_plan.new_meal import CreatePlanEntry
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/groups/mealplans"
    recipe = "/api/recipes"
    today = "/api/groups/mealplans/today"

    def item(item_id: int) -> str:
        return f"{Routes.base}/{item_id}"

    def recipe_slug(recipe_id: int) -> str:
        return f"{Routes.recipe}/{recipe_id}"


def test_create_mealplan_no_recipe(api_client: TestClient, unique_user: TestUser):
    title = random_string(length=25)
    text = random_string(length=25)
    new_plan = CreatePlanEntry(date=date.today(), entry_type="breakfast", title=title, text=text).dict()
    new_plan["date"] = date.today().strftime("%Y-%m-%d")

    response = api_client.post(Routes.base, json=new_plan, headers=unique_user.token)

    assert response.status_code == 201

    response_json = response.json()
    assert response_json["title"] == title
    assert response_json["text"] == text


def test_create_mealplan_with_recipe(api_client: TestClient, unique_user: TestUser):
    recipe_name = random_string(length=25)
    response = api_client.post(Routes.recipe, json={"name": recipe_name}, headers=unique_user.token)
    assert response.status_code == 201

    response = api_client.get(Routes.recipe_slug(recipe_name), headers=unique_user.token)
    recipe = response.json()
    recipe_id = recipe["id"]

    new_plan = CreatePlanEntry(date=date.today(), entry_type="dinner", recipe_id=recipe_id).dict(by_alias=True)
    new_plan["date"] = date.today().strftime("%Y-%m-%d")

    response = api_client.post(Routes.base, json=new_plan, headers=unique_user.token)
    response_json = response.json()
    assert response.status_code == 201

    assert response_json["recipe"]["slug"] == recipe_name


def test_crud_mealplan(api_client: TestClient, unique_user: TestUser):
    new_plan = CreatePlanEntry(
        date=date.today(),
        entry_type="breakfast",
        title=random_string(),
        text=random_string(),
    ).dict()

    # Create
    new_plan["date"] = date.today().strftime("%Y-%m-%d")
    response = api_client.post(Routes.base, json=new_plan, headers=unique_user.token)
    response_json = response.json()
    assert response.status_code == 201
    plan_id = response_json["id"]

    # Update
    response_json["title"] = random_string()
    response_json["text"] = random_string()

    response = api_client.put(Routes.item(plan_id), headers=unique_user.token, json=response_json)

    assert response.status_code == 200

    assert response.json()["title"] == response_json["title"]
    assert response.json()["text"] == response_json["text"]

    # Delete
    response = api_client.delete(Routes.item(plan_id), headers=unique_user.token)

    assert response.status_code == 200

    response = api_client.get(Routes.item(plan_id), headers=unique_user.token)
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
        response = api_client.post(Routes.base, json=new_plan, headers=unique_user.token)
        assert response.status_code == 201

    response = api_client.get(Routes.base, headers=unique_user.token)

    assert response.status_code == 200
    assert len(response.json()) >= 3


def test_get_slice_mealplans():
    assert False


def test_get_mealplan_today():
    assert False
