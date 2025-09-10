import random
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient

from mealie.schema.household.household import HouseholdSummary
from mealie.schema.meal_plan.new_meal import CreatePlanEntry
from mealie.schema.meal_plan.plan_rules import PlanRulesDay, PlanRulesOut, PlanRulesSave, PlanRulesType
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_category import CategoryOut, CategorySave, TagOut, TagSave
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def route_all_slice(page: int, perPage: int, start_date: str, end_date: str):
    return (
        f"{api_routes.households_mealplans}?page={page}&perPage={perPage}&start_date={start_date}&end_date={end_date}"
    )


def create_recipe(unique_user: TestUser, tags: list[TagOut] | None = None, categories: list[CategoryOut] | None = None):
    return unique_user.repos.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=UUID(unique_user.group_id),
            name=random_string(),
            tags=tags or [],
            recipe_category=categories or [],
        )
    )


def create_rule(
    unique_user: TestUser,
    day: PlanRulesDay,
    entry_type: PlanRulesType,
    tags: list[TagOut] | None = None,
    categories: list[CategoryOut] | None = None,
    households: list[HouseholdSummary] | None = None,
):
    qf_parts: list[str] = []
    if tags:
        qf_parts.append(f"tags.id CONTAINS ALL [{','.join([str(tag.id) for tag in tags])}]")
    if categories:
        qf_parts.append(f"recipe_category.id CONTAINS ALL [{','.join([str(cat.id) for cat in categories])}]")
    if households:
        qf_parts.append(f"household_id IN [{','.join([str(household.id) for household in households])}]")

    query_filter_string = " AND ".join(qf_parts)
    return unique_user.repos.group_meal_plan_rules.create(
        PlanRulesSave(
            group_id=UUID(unique_user.group_id),
            household_id=UUID(unique_user.household_id),
            day=day,
            entry_type=entry_type,
            query_filter_string=query_filter_string,
        )
    )


def test_create_mealplan_no_recipe(api_client: TestClient, unique_user: TestUser):
    title = random_string(length=25)
    text = random_string(length=25)
    new_plan = CreatePlanEntry(
        date=datetime.now(UTC).date(), entry_type="breakfast", title=title, text=text
    ).model_dump()
    new_plan["date"] = datetime.now(UTC).date().strftime("%Y-%m-%d")

    response = api_client.post(api_routes.households_mealplans, json=new_plan, headers=unique_user.token)

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

    new_plan = CreatePlanEntry(date=datetime.now(UTC).date(), entry_type="dinner", recipe_id=recipe_id).model_dump(
        by_alias=True
    )
    new_plan["date"] = datetime.now(UTC).date().strftime("%Y-%m-%d")
    new_plan["recipeId"] = str(recipe_id)

    response = api_client.post(api_routes.households_mealplans, json=new_plan, headers=unique_user.token)
    response_json = response.json()
    assert response.status_code == 201

    assert response_json["recipe"]["slug"] == recipe_name


def test_crud_mealplan(api_client: TestClient, unique_user: TestUser):
    new_plan = CreatePlanEntry(
        date=datetime.now(UTC).date(),
        entry_type="breakfast",
        title=random_string(),
        text=random_string(),
    ).model_dump()

    # Create
    new_plan["date"] = datetime.now(UTC).date().strftime("%Y-%m-%d")
    response = api_client.post(api_routes.households_mealplans, json=new_plan, headers=unique_user.token)
    response_json = response.json()
    assert response.status_code == 201
    plan_id = response_json["id"]

    # Update
    response_json["title"] = random_string()
    response_json["text"] = random_string()

    response = api_client.put(
        api_routes.households_mealplans_item_id(plan_id), headers=unique_user.token, json=response_json
    )

    assert response.status_code == 200

    assert response.json()["title"] == response_json["title"]
    assert response.json()["text"] == response_json["text"]

    # Delete
    response = api_client.delete(api_routes.households_mealplans_item_id(plan_id), headers=unique_user.token)

    assert response.status_code == 200

    response = api_client.get(api_routes.households_mealplans_item_id(plan_id), headers=unique_user.token)
    assert response.status_code == 404


def test_get_all_mealplans(api_client: TestClient, unique_user: TestUser):
    for _ in range(3):
        new_plan = CreatePlanEntry(
            date=datetime.now(UTC).date(),
            entry_type="breakfast",
            title=random_string(),
            text=random_string(),
        ).model_dump()

        new_plan["date"] = datetime.now(UTC).date().strftime("%Y-%m-%d")
        response = api_client.post(api_routes.households_mealplans, json=new_plan, headers=unique_user.token)
        assert response.status_code == 201

    response = api_client.get(
        api_routes.households_mealplans, headers=unique_user.token, params={"page": 1, "perPage": -1}
    )

    assert response.status_code == 200
    assert len(response.json()["items"]) >= 3


def test_get_slice_mealplans(api_client: TestClient, unique_user: TestUser):
    # Make List of 10 dates from now to +10 days
    dates = [datetime.now(UTC).date() + timedelta(days=x) for x in range(10)]

    # Make a list of 10 meal plans
    meal_plans = [
        CreatePlanEntry(date=date, entry_type="breakfast", title=random_string(), text=random_string()).model_dump()
        for date in dates
    ]

    # Add the meal plans to the database
    for meal_plan in meal_plans:
        meal_plan["date"] = meal_plan["date"].strftime("%Y-%m-%d")
        response = api_client.post(api_routes.households_mealplans, json=meal_plan, headers=unique_user.token)
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
        CreatePlanEntry(
            date=datetime.now(UTC).date(), entry_type="breakfast", title=random_string(), text=random_string()
        ).model_dump()
        for _ in range(3)
    ]

    # Add the meal plans to the database
    for meal_plan in test_meal_plans:
        meal_plan["date"] = meal_plan["date"].strftime("%Y-%m-%d")
        response = api_client.post(api_routes.households_mealplans, json=meal_plan, headers=unique_user.token)
        assert response.status_code == 201

    # Get meal plan for today
    response = api_client.get(api_routes.households_mealplans_today, headers=unique_user.token)

    assert response.status_code == 200

    response_json = response.json()

    for meal_plan in response_json:
        assert meal_plan["date"] == datetime.now(UTC).date().strftime("%Y-%m-%d")


def test_get_mealplan_with_rules_categories_and_tags_filter(api_client: TestClient, unique_user: TestUser):
    tags = [
        unique_user.repos.tags.create(TagSave(name=random_string(), group_id=unique_user.group_id)) for _ in range(4)
    ]
    categories = [
        unique_user.repos.categories.create(CategorySave(name=random_string(), group_id=unique_user.group_id))
        for _ in range(4)
    ]
    [
        create_recipe(unique_user, tags=[tag], categories=[category])
        for tag, category in zip(tags, categories, strict=True)
    ]
    [create_recipe(unique_user) for _ in range(5)]

    i = random.randint(0, 3)
    tag = tags[i]
    category = categories[i]
    rule = create_rule(
        unique_user,
        day=PlanRulesDay.saturday,
        entry_type=PlanRulesType.breakfast,
        tags=[tag],
        categories=[category],
    )

    try:
        payload = {"date": "2023-02-25", "entryType": "breakfast"}
        response = api_client.post(api_routes.households_mealplans_random, json=payload, headers=unique_user.token)
        assert response.status_code == 200
        recipe_data = response.json()["recipe"]
        assert recipe_data["tags"][0]["name"] == tag.name
        assert recipe_data["recipeCategory"][0]["name"] == category.name
    finally:
        unique_user.repos.group_meal_plan_rules.delete(rule.id)


def test_get_mealplan_with_rules_date_and_type_filter(api_client: TestClient, unique_user: TestUser):
    tags = [
        unique_user.repos.tags.create(TagSave(name=random_string(), group_id=unique_user.group_id)) for _ in range(4)
    ]
    recipes = [create_recipe(unique_user, tags=[tag]) for tag in tags]
    [create_recipe(unique_user) for _ in range(5)]

    rules: list[PlanRulesOut] = []
    rules.append(
        create_rule(unique_user, day=PlanRulesDay.saturday, entry_type=PlanRulesType.breakfast, tags=[tags[0]])
    )
    rules.append(create_rule(unique_user, day=PlanRulesDay.saturday, entry_type=PlanRulesType.dinner, tags=[tags[1]]))
    rules.append(create_rule(unique_user, day=PlanRulesDay.sunday, entry_type=PlanRulesType.breakfast, tags=[tags[2]]))
    rules.append(create_rule(unique_user, day=PlanRulesDay.sunday, entry_type=PlanRulesType.dinner, tags=[tags[3]]))

    try:
        payload = {"date": "2023-02-25", "entryType": "breakfast"}
        response = api_client.post(api_routes.households_mealplans_random, json=payload, headers=unique_user.token)
        assert response.status_code == 200
        assert response.json()["recipe"]["slug"] == recipes[0].slug
    finally:
        for rule in rules:
            unique_user.repos.group_meal_plan_rules.delete(rule.id)


def test_get_mealplan_with_rules_includes_other_households(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser
):
    tag = h2_user.repos.tags.create(TagSave(name=random_string(), group_id=h2_user.group_id))
    recipe = create_recipe(h2_user, tags=[tag])
    rule = create_rule(unique_user, day=PlanRulesDay.saturday, entry_type=PlanRulesType.breakfast, tags=[tag])

    try:
        payload = {"date": "2023-02-25", "entryType": "breakfast"}
        response = api_client.post(api_routes.households_mealplans_random, json=payload, headers=unique_user.token)
        assert response.status_code == 200
        assert response.json()["recipe"]["slug"] == recipe.slug
    finally:
        unique_user.repos.group_meal_plan_rules.delete(rule.id)


def test_get_mealplan_with_rules_households_filter(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    tag = unique_user.repos.tags.create(TagSave(name=random_string(), group_id=unique_user.group_id))
    recipe = create_recipe(unique_user, tags=[tag])
    [create_recipe(h2_user, tags=[tag]) for _ in range(10)]

    household = unique_user.repos.households.get_by_slug_or_id(unique_user.household_id)
    assert household

    rule = create_rule(
        unique_user, day=PlanRulesDay.saturday, entry_type=PlanRulesType.breakfast, tags=[tag], households=[household]
    )

    try:
        payload = {"date": "2023-02-25", "entryType": "breakfast"}
        response = api_client.post(api_routes.households_mealplans_random, json=payload, headers=unique_user.token)
        assert response.status_code == 200
        assert response.json()["recipe"]["slug"] == recipe.slug
    finally:
        unique_user.repos.group_meal_plan_rules.delete(rule.id)


def test_get_mealplan_with_rules_households_filter_includes_any_households(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser
):
    tag = unique_user.repos.tags.create(TagSave(name=random_string(), group_id=unique_user.group_id))
    recipe = create_recipe(h2_user, tags=[tag])

    household = unique_user.repos.households.get_by_slug_or_id(unique_user.household_id)
    assert household
    h2_household = unique_user.repos.households.get_by_slug_or_id(h2_user.household_id)
    assert h2_household
    rule = create_rule(
        unique_user,
        day=PlanRulesDay.saturday,
        entry_type=PlanRulesType.breakfast,
        tags=[tag],
        households=[household, h2_household],
    )

    try:
        payload = {"date": "2023-02-25", "entryType": "breakfast"}
        response = api_client.post(api_routes.households_mealplans_random, json=payload, headers=unique_user.token)
        assert response.status_code == 200
        assert response.json()["recipe"]["slug"] == recipe.slug
    finally:
        unique_user.repos.group_meal_plan_rules.delete(rule.id)
