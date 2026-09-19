from datetime import date
from uuid import UUID

from fastapi.testclient import TestClient

from mealie.schema.household.household_preferences import UpdateHouseholdPreferences
from mealie.schema.meal_plan.new_meal import CreatePlanEntry
from mealie.schema.recipe.recipe import Recipe
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def enable_feed(api_client: TestClient, user: TestUser) -> str:
    response = api_client.post(api_routes.households_mealplans_ical, headers=user.token)
    assert response.status_code == 200
    token = response.json()["mealplanIcalToken"]
    assert token
    return token


def get_feed(api_client: TestClient, token: str, params: dict | None = None):
    # the feed is public, so no auth headers are sent
    return api_client.get(api_routes.households_mealplans_ical_token(token), params=params)


def unfold(feed: str) -> str:
    return feed.replace("\r\n ", "")


def create_entry(api_client: TestClient, user: TestUser, **kwargs) -> dict:
    data = CreatePlanEntry(**kwargs).model_dump(by_alias=True, mode="json")
    response = api_client.post(api_routes.households_mealplans, json=data, headers=user.token)
    assert response.status_code == 201
    return response.json()


def test_ical_feed_disabled_by_default(api_client: TestClient, unique_user_fn_scoped: TestUser):
    response = api_client.get(api_routes.households_mealplans_ical, headers=unique_user_fn_scoped.token)
    assert response.status_code == 200
    assert response.json()["mealplanIcalToken"] is None

    assert get_feed(api_client, random_string(32)).status_code == 404


def test_ical_feed(api_client: TestClient, unique_user_fn_scoped: TestUser, h2_user: TestUser):
    user = unique_user_fn_scoped
    recipe = user.repos.recipes.create(Recipe(user_id=user.user_id, group_id=UUID(user.group_id), name=random_string()))
    group = user.repos.groups.get_one(UUID(user.group_id))
    assert group

    create_entry(api_client, user, date=date(2026, 7, 1), entry_type="dinner", recipe_id=recipe.id)
    create_entry(api_client, user, date=date(2026, 7, 2), entry_type="lunch", title="Leftovers, again; sorry")
    other = create_entry(api_client, h2_user, date=date(2026, 7, 1), entry_type="dinner", title=random_string())

    token = enable_feed(api_client, user)
    response = get_feed(api_client, token)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/calendar")

    feed = response.text
    assert feed.startswith("BEGIN:VCALENDAR\r\n")
    assert feed.endswith("END:VCALENDAR\r\n")
    assert all(len(line.encode()) <= 75 for line in feed.split("\r\n"))

    feed = unfold(feed)
    assert feed.count("BEGIN:VEVENT") == 2
    assert f"SUMMARY:Dinner: {recipe.name}\r\n" in feed
    assert f"URL:http://localhost:8080/g/{group.slug}/r/{recipe.slug}\r\n" in feed
    assert "DTSTART;VALUE=DATE:20260701\r\nDTEND;VALUE=DATE:20260702\r\n" in feed
    assert "SUMMARY:Lunch: Leftovers\\, again\\; sorry\r\n" in feed

    # meals from other households are never included
    assert other["title"] not in feed


def test_ical_feed_filters_and_times(api_client: TestClient, unique_user_fn_scoped: TestUser):
    user = unique_user_fn_scoped
    recipe = user.repos.recipes.create(Recipe(user_id=user.user_id, group_id=UUID(user.group_id), name=random_string()))
    create_entry(api_client, user, date=date(2026, 7, 1), entry_type="dinner", recipe_id=recipe.id)
    create_entry(api_client, user, date=date(2026, 7, 1), entry_type="breakfast", recipe_id=recipe.id)
    note = create_entry(api_client, user, date=date(2026, 7, 1), entry_type="dinner", title=random_string())
    token = enable_feed(api_client, user)

    feed = unfold(get_feed(api_client, token, {"types": ["dinner"]}).text)
    assert feed.count("BEGIN:VEVENT") == 2
    assert "SUMMARY:Breakfast" not in feed

    feed = unfold(get_feed(api_client, token, {"types": ["dinner"], "includeNotes": False}).text)
    assert feed.count("BEGIN:VEVENT") == 1
    assert note["title"] not in feed

    # Berlin is UTC+2 in July; types without a time stay all-day events
    feed = unfold(get_feed(api_client, token, {"tz": "Europe/Berlin", "dinner": "18:30"}).text)
    assert "DTSTART:20260701T163000Z\r\nDTEND:20260701T173000Z\r\n" in feed
    assert "DTSTART;VALUE=DATE:20260701\r\n" in feed

    assert get_feed(api_client, token, {"tz": "Not/AZone"}).status_code == 422
    assert get_feed(api_client, token, {"types": ["brunch"]}).status_code == 422


def test_ical_token_rotate_and_disable(api_client: TestClient, unique_user_fn_scoped: TestUser):
    user = unique_user_fn_scoped
    old_token = enable_feed(api_client, user)
    new_token = enable_feed(api_client, user)
    assert new_token != old_token

    assert get_feed(api_client, old_token).status_code == 404
    assert get_feed(api_client, new_token).status_code == 200

    response = api_client.delete(api_routes.households_mealplans_ical, headers=user.token)
    assert response.status_code == 200
    assert response.json()["mealplanIcalToken"] is None
    assert get_feed(api_client, new_token).status_code == 404


def test_ical_token_not_exposed_or_cleared_by_preferences(api_client: TestClient, unique_user_fn_scoped: TestUser):
    user = unique_user_fn_scoped
    token = enable_feed(api_client, user)

    response = api_client.get(api_routes.households_self, headers=user.token)
    assert token not in response.text
    response = api_client.get(api_routes.households_preferences, headers=user.token)
    assert token not in response.text

    response = api_client.put(
        api_routes.households_preferences,
        json=UpdateHouseholdPreferences(first_day_of_week=1).model_dump(by_alias=True),
        headers=user.token,
    )
    assert response.status_code == 200
    assert get_feed(api_client, token).status_code == 200


def test_ical_token_requires_manage_household(api_client: TestClient, user_tuple: list[TestUser]):
    manager, member = user_tuple
    for test_user, can_manage in [(manager, True), (member, False)]:
        user = test_user.repos.users.get_one(test_user.user_id)
        assert user
        user.can_manage_household = can_manage
        test_user.repos.users.update(user.id, user)

    token = enable_feed(api_client, manager)

    response = api_client.get(api_routes.households_mealplans_ical, headers=member.token)
    assert response.status_code == 200
    assert response.json()["mealplanIcalToken"] == token

    assert api_client.post(api_routes.households_mealplans_ical, headers=member.token).status_code == 403
    assert api_client.delete(api_routes.households_mealplans_ical, headers=member.token).status_code == 403
    assert get_feed(api_client, token).status_code == 200
