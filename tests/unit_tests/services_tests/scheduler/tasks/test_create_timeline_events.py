from datetime import UTC, datetime, timedelta

from dateutil.parser import parse as parse_dt
from fastapi.testclient import TestClient
from pydantic import UUID4

from mealie.schema.household.household import HouseholdRecipeSummary
from mealie.schema.meal_plan.new_meal import CreatePlanEntry
from mealie.schema.recipe.recipe import RecipeLastMade, RecipeSummary
from mealie.services.scheduler.tasks.create_timeline_events import create_mealplan_timeline_events
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


def test_no_mealplans():
    # make sure this task runs successfully even if it doesn't do anything
    create_mealplan_timeline_events()


def test_new_mealplan_event(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    recipe_name = random_string(length=25)
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=unique_user.token)
    assert response.status_code == 201

    response = api_client.get(api_routes.recipes_slug(recipe_name), headers=unique_user.token)
    original_recipe_data: dict = response.json()
    recipe = RecipeSummary.model_validate(original_recipe_data)
    recipe_id = recipe.id
    assert recipe.last_made is None

    # store the number of events, so we can compare later
    params = {"queryFilter": f"recipe_id={recipe_id}"}
    response = api_client.get(api_routes.recipes_timeline_events, params=params, headers=unique_user.token)
    response_json = response.json()
    initial_event_count = len(response_json["items"])

    new_plan = CreatePlanEntry(date=datetime.now(UTC).date(), entry_type="dinner", recipe_id=recipe_id).model_dump(
        by_alias=True
    )
    new_plan["date"] = datetime.now(UTC).date().isoformat()
    new_plan["recipeId"] = str(recipe_id)

    response = api_client.post(api_routes.households_mealplans, json=new_plan, headers=unique_user.token)
    assert response.status_code == 201

    # run the task and check to make sure a new event was created from the mealplan
    create_mealplan_timeline_events()

    params = {
        "page": "1",
        "perPage": "-1",
        "orderBy": "created_at",
        "orderDirection": "desc",
        "queryFilter": f"recipe_id={recipe_id}",
    }
    response = api_client.get(api_routes.recipes_timeline_events, headers=unique_user.token, params=params)
    response_json = response.json()
    assert len(response_json["items"]) == initial_event_count + 1

    # make sure the mealplan entry type is in the subject
    event = response_json["items"][0]
    assert new_plan["entryType"].lower() in event["subject"].lower()

    # make sure the recipe's last made date was updated
    response = api_client.get(api_routes.recipes_slug(recipe_name), headers=unique_user.token)
    new_recipe_data: dict = response.json()
    recipe = RecipeSummary.model_validate(new_recipe_data)
    assert recipe.last_made and recipe.last_made.date() == datetime.now(UTC).date()

    # make sure nothing else was updated
    for data in [original_recipe_data, new_recipe_data]:
        data.pop("dateUpdated")
        data.pop("updatedAt")
        data.pop("lastMade")

    # instructions ids are generated randomly and aren't consistent between get requests
    old_instructions: list[dict] = original_recipe_data.pop("recipeInstructions")
    new_instructions: list[dict] = new_recipe_data.pop("recipeInstructions")
    assert len(old_instructions) == len(new_instructions)

    for old, new in zip(old_instructions, new_instructions, strict=True):
        old.pop("id")
        new.pop("id")
        assert old == new

    assert original_recipe_data == new_recipe_data

    # make sure the user's last made date was updated
    response = api_client.get(api_routes.households_self_recipes_recipe_slug(recipe_name), headers=unique_user.token)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["lastMade"]
    assert parse_dt(response_json["lastMade"]).date() == datetime.now(UTC).date()

    # make sure the other user's last made date was not updated
    response = api_client.get(api_routes.households_self_recipes_recipe_slug(recipe_name), headers=h2_user.token)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["lastMade"] is None


def test_new_mealplan_event_duplicates(api_client: TestClient, unique_user: TestUser):
    recipe_name = random_string(length=25)
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=unique_user.token)
    assert response.status_code == 201

    response = api_client.get(api_routes.recipes_slug(recipe_name), headers=unique_user.token)
    recipe = RecipeSummary.model_validate(response.json())
    recipe_id = recipe.id

    # store the number of events, so we can compare later
    params = {"queryFilter": f"recipe_id={recipe_id}"}
    response = api_client.get(api_routes.recipes_timeline_events, params=params, headers=unique_user.token)
    response_json = response.json()
    initial_event_count = len(response_json["items"])

    new_plan = CreatePlanEntry(date=datetime.now(UTC).date(), entry_type="dinner", recipe_id=recipe_id).model_dump(
        by_alias=True
    )
    new_plan["date"] = datetime.now(UTC).date().isoformat()
    new_plan["recipeId"] = str(recipe_id)

    response = api_client.post(api_routes.households_mealplans, json=new_plan, headers=unique_user.token)
    assert response.status_code == 201

    # run the task multiple times and make sure we only create one event
    for _ in range(3):
        create_mealplan_timeline_events()

    params = {
        "page": "1",
        "perPage": "-1",
        "orderBy": "created_at",
        "orderDirection": "desc",
        "queryFilter": f"recipe_id={recipe_id}",
    }
    response = api_client.get(api_routes.recipes_timeline_events, headers=unique_user.token, params=params)
    response_json = response.json()
    assert len(response_json["items"]) == initial_event_count + 1


def test_new_mealplan_events_with_multiple_recipes(api_client: TestClient, unique_user: TestUser):
    recipes: list[RecipeSummary] = []
    for _ in range(3):
        recipe_name = random_string(length=25)
        response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=unique_user.token)
        assert response.status_code == 201

        response = api_client.get(api_routes.recipes_slug(recipe_name), headers=unique_user.token)
        recipes.append(RecipeSummary.model_validate(response.json()))

    # store the number of events, so we can compare later
    params = {"queryFilter": f"recipe_id={recipes[0].id}"}
    response = api_client.get(api_routes.recipes_timeline_events, params=params, headers=unique_user.token)
    response_json = response.json()
    initial_event_count = len(response_json["items"])

    # create a few mealplans for each recipe
    mealplan_count_by_recipe_id: dict[UUID4, int] = {}
    for recipe in recipes:
        mealplan_count_by_recipe_id[recipe.id] = 0  # type: ignore
        for _ in range(random_int(1, 5)):
            new_plan = CreatePlanEntry(
                date=datetime.now(UTC).date(), entry_type="dinner", recipe_id=str(recipe.id)
            ).model_dump(by_alias=True)
            new_plan["date"] = datetime.now(UTC).date().isoformat()
            new_plan["recipeId"] = str(recipe.id)

            response = api_client.post(api_routes.households_mealplans, json=new_plan, headers=unique_user.token)
            assert response.status_code == 201
            mealplan_count_by_recipe_id[recipe.id] += 1  # type: ignore

    # run the task once and make sure the event counts are correct
    create_mealplan_timeline_events()

    for recipe in recipes:
        target_count = initial_event_count + mealplan_count_by_recipe_id[recipe.id]  # type: ignore
        params = {
            "page": "1",
            "perPage": "-1",
            "orderBy": "created_at",
            "orderDirection": "desc",
            "queryFilter": f"recipe_id={recipe.id}",
        }
        response = api_client.get(api_routes.recipes_timeline_events, headers=unique_user.token, params=params)
        response_json = response.json()
        assert len(response_json["items"]) == target_count

    # run the task a few more times and confirm the counts are the same
    for _ in range(3):
        create_mealplan_timeline_events()

    for recipe in recipes:
        target_count = initial_event_count + mealplan_count_by_recipe_id[recipe.id]  # type: ignore
        params = {
            "page": "1",
            "perPage": "-1",
            "orderBy": "created_at",
            "orderDirection": "desc",
            "queryFilter": f"recipe_id={recipe.id}",
        }
        response = api_client.get(api_routes.recipes_timeline_events, headers=unique_user.token, params=params)
        response_json = response.json()
        assert len(response_json["items"]) == target_count


def test_preserve_future_made_date(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    recipe_name = random_string(length=25)
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=unique_user.token)
    assert response.status_code == 201

    response = api_client.get(api_routes.recipes_slug(recipe_name), headers=unique_user.token)
    recipe = RecipeSummary.model_validate(response.json())
    recipe_id = str(recipe.id)

    future_dt = datetime.now(UTC) + timedelta(days=random_int(1, 10))
    response = api_client.patch(
        api_routes.recipes_slug_last_made(recipe.slug),
        data=RecipeLastMade(timestamp=future_dt).model_dump_json(),
        headers=unique_user.token,
    )
    assert response.status_code == 200

    # verify the last made date was updated only on unique_user
    response = api_client.get(api_routes.households_self_recipes_recipe_slug(recipe.slug), headers=unique_user.token)
    household_recipe = HouseholdRecipeSummary.model_validate(response.json())
    assert household_recipe.last_made == future_dt

    response = api_client.get(api_routes.households_self_recipes_recipe_slug(recipe.slug), headers=h2_user.token)
    household_recipe = HouseholdRecipeSummary.model_validate(response.json())
    assert household_recipe.last_made is None

    new_plan = CreatePlanEntry(date=datetime.now(UTC).date(), entry_type="dinner", recipe_id=recipe_id).model_dump(
        by_alias=True
    )
    new_plan["date"] = datetime.now(UTC).date().isoformat()
    new_plan["recipeId"] = str(recipe_id)

    response = api_client.post(api_routes.households_mealplans, json=new_plan, headers=unique_user.token)
    assert response.status_code == 201

    # run the task and make sure the recipe's last made date was not updated for either user
    create_mealplan_timeline_events()

    response = api_client.get(api_routes.households_self_recipes_recipe_slug(recipe.slug), headers=unique_user.token)
    assert response.status_code == 200
    household_recipe = HouseholdRecipeSummary.model_validate(response.json())
    assert household_recipe.last_made == future_dt

    response = api_client.get(api_routes.households_self_recipes_recipe_slug(recipe.slug), headers=h2_user.token)
    household_recipe = HouseholdRecipeSummary.model_validate(response.json())
    assert household_recipe.last_made is None
