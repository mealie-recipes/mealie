from datetime import UTC, datetime, timedelta
from uuid import UUID

from pydantic import UUID4

from mealie.schema.household.webhook import SaveWebhook, WebhookType
from mealie.services.event_bus_service.event_bus_listeners import WebhookEventListener
from mealie.services.event_bus_service.event_types import (
    Event,
    EventBusMessage,
    EventDocumentType,
    EventTypes,
    EventWebhookData,
)
from tests.utils import random_string
from tests.utils.factories import random_bool
from tests.utils.fixture_schemas import TestUser


def webhook_factory(
    group_id: str | UUID4,
    household_id: str | UUID4,
    enabled: bool = True,
    name: str = "",
    url: str = "",
    scheduled_time: datetime | None = None,
    webhook_type: str = WebhookType.mealplan,
) -> SaveWebhook:
    return SaveWebhook(
        enabled=enabled,
        name=name or random_string(),
        url=url or random_string(),
        webhook_type=webhook_type,
        scheduled_time=scheduled_time.time() if scheduled_time else datetime.now(UTC).time(),
        group_id=group_id,
        household_id=household_id,
    )


def test_get_scheduled_webhooks_filter_query(unique_user: TestUser):
    """
    get_scheduled_webhooks_test tests the get_scheduled_webhooks function on the webhook event bus listener.
    """

    database = unique_user.repos
    expected: list[SaveWebhook] = []

    start = datetime.now(UTC)

    for _ in range(5):
        new_item = webhook_factory(
            group_id=unique_user.group_id, household_id=unique_user.household_id, enabled=random_bool()
        )
        out_of_range_item = webhook_factory(
            group_id=unique_user.group_id,
            household_id=unique_user.household_id,
            enabled=random_bool(),
            scheduled_time=(start - timedelta(minutes=20)),
        )

        database.webhooks.create(new_item)
        database.webhooks.create(out_of_range_item)

        if new_item.enabled:
            expected.append(new_item)

    event_bus_listener = WebhookEventListener(UUID(unique_user.group_id), UUID(unique_user.household_id))
    results = event_bus_listener.get_scheduled_webhooks(start, datetime.now(UTC) + timedelta(minutes=5))

    assert len(results) == len(expected)

    for result in results:
        assert result.enabled

        for expected_item in expected:
            if result.name == expected_item.name:  # Names are uniquely generated so we can use this to compare
                assert result.enabled == expected_item.enabled
                break


def test_event_listener_get_meals_by_date_range(unique_user: TestUser):
    """
    Test that WebhookEventListener correctly uses the get_meals_by_date_range method
    to retrieve meals and publish the webhook event.
    """
    meal_repo = unique_user.repos.meals

    start_date = datetime.now(UTC) - timedelta(days=7)
    end_date = datetime.now(UTC)

    meal_1 = meal_repo.create(
        {
            "date": start_date + timedelta(days=1),
            "entry_type": "lunch",
            "title": "Meal 1",
            "text": "Test meal 1",
            "group_id": unique_user.group_id,
            "household_id": unique_user.household_id,
            "user_id": unique_user.user_id,
        }
    )
    meal_2 = meal_repo.create(
        {
            "date": start_date + timedelta(days=3),
            "entry_type": "dinner",
            "title": "Meal 2",
            "text": "Test meal 2",
            "group_id": unique_user.group_id,
            "household_id": unique_user.household_id,
            "user_id": unique_user.user_id,
        }
    )

    webhook_data = EventWebhookData(
        webhook_start_dt=start_date,
        webhook_end_dt=end_date,
        document_type=EventDocumentType.mealplan,
        operation="create",
    )
    event = Event(
        event_type=EventTypes.webhook_task,
        document_data=webhook_data,
        message=EventBusMessage(title="Test event message"),
        integration_id="00000000-0000-0000-0000-000000000000",
    )

    event_bus_listener = WebhookEventListener(UUID(unique_user.group_id), UUID(unique_user.household_id))
    subscribers = event_bus_listener.get_scheduled_webhooks(start_date, end_date)

    event_bus_listener.publish_to_subscribers(event, subscribers)

    assert event.document_data.webhook_body is not None
    meals = event.document_data.webhook_body
    assert len(meals) == 2

    assert any(meal.title == "Meal 1" for meal in meals)
    assert any(meal.title == "Meal 2" for meal in meals)

    try:
        assert event.document_data.webhook_body is not None
        meals = event.document_data.webhook_body
        assert len(meals) == 2

        assert any(meal.title == "Meal 1" for meal in meals)
        assert any(meal.title == "Meal 2" for meal in meals)

    finally:
        meal_repo.delete(meal_1.id)
        meal_repo.delete(meal_2.id)


def test_get_meals_by_date_range(unique_user: TestUser):
    meal_repo = unique_user.repos.meals

    start_date = datetime.now(UTC) - timedelta(days=7)
    end_date = datetime.now(UTC)

    meal_1 = meal_repo.create(
        {
            "date": start_date + timedelta(days=1),
            "entry_type": "breakfast",
            "title": "Meal 1",
            "text": "Test meal 1",
            "group_id": unique_user.group_id,
            "household_id": unique_user.household_id,
            "user_id": unique_user.user_id,
        }
    )
    meal_2 = meal_repo.create(
        {
            "date": start_date + timedelta(days=3),
            "entry_type": "lunch",
            "title": "Meal 2",
            "text": "Test meal 2",
            "group_id": unique_user.group_id,
            "household_id": unique_user.household_id,
            "user_id": unique_user.user_id,
        }
    )
    meal_3 = meal_repo.create(
        {
            "date": start_date - timedelta(days=10),
            "entry_type": "dinner",
            "title": "Meal 3",
            "text": "Test meal 3",
            "group_id": unique_user.group_id,
            "household_id": unique_user.household_id,
            "user_id": unique_user.user_id,
        }
    )

    try:
        meals_in_range = meal_repo.get_meals_by_date_range(start_date, end_date)

        assert len(meals_in_range) == 2
        assert any(meal.title == "Meal 1" for meal in meals_in_range)
        assert any(meal.title == "Meal 2" for meal in meals_in_range)

        assert all(meal.title != "Meal 3" for meal in meals_in_range)

    finally:
        meal_repo.delete(meal_1.id)
        meal_repo.delete(meal_2.id)
        meal_repo.delete(meal_3.id)


def test_get_meals_by_date_range_no_meals(unique_user: TestUser):
    """
    Test that get_meals_by_date_range returns an empty list when there are no meals in the given date range.
    """
    meal_repo = unique_user.repos.meals

    start_date = datetime.now(UTC) - timedelta(days=7)
    end_date = datetime.now(UTC)

    meals_in_range = meal_repo.get_meals_by_date_range(start_date, end_date)

    assert len(meals_in_range) == 0


def test_get_meals_by_date_range_single_day(unique_user: TestUser):
    """
    Test that get_meals_by_date_range returns meals correctly when start_date and end_date are the same.
    """
    meal_repo = unique_user.repos.meals

    single_day = datetime.now(UTC)

    meal_1 = meal_repo.create(
        {
            "date": single_day,
            "entry_type": "breakfast",
            "title": "Single Day Meal",
            "text": "Test meal for a single day",
            "group_id": unique_user.group_id,
            "household_id": unique_user.household_id,
            "user_id": unique_user.user_id,
        }
    )

    try:
        meals_in_range = meal_repo.get_meals_by_date_range(single_day, single_day)

        assert len(meals_in_range) == 1
        assert meals_in_range[0].title == "Single Day Meal"
        assert meals_in_range[0].date == single_day.date()

    finally:
        meal_repo.delete(meal_1.id)


def test_get_meals_by_date_range_no_overlap(unique_user: TestUser):
    """
    Test that get_meals_by_date_range returns an empty list when there are no meals that overlap with the date range.
    """
    meal_repo = unique_user.repos.meals

    start_date = datetime.now(UTC) + timedelta(days=1)
    end_date = datetime.now(UTC) + timedelta(days=10)

    meal_1 = meal_repo.create(
        {
            "date": datetime.now(UTC) - timedelta(days=5),
            "entry_type": "dinner",
            "title": "Meal Outside Range",
            "text": "This meal is outside the tested date range",
            "group_id": unique_user.group_id,
            "household_id": unique_user.household_id,
            "user_id": unique_user.user_id,
        }
    )

    meals_in_range = meal_repo.get_meals_by_date_range(start_date, end_date)

    assert len(meals_in_range) == 0

    try:
        meals_in_range = meal_repo.get_meals_by_date_range(start_date, end_date)

        assert len(meals_in_range) == 0

    finally:
        meal_repo.delete(meal_1.id)


def test_get_meals_by_date_range_invalid_date_range(unique_user: TestUser):
    """
    Test that get_meals_by_date_range raises an exception or returns empty when start_date is greater than end_date.
    """
    meal_repo = unique_user.repos.meals

    start_date = datetime.now(UTC)
    end_date = start_date - timedelta(days=1)

    meals_in_range = meal_repo.get_meals_by_date_range(start_date, end_date)

    assert len(meals_in_range) == 0
