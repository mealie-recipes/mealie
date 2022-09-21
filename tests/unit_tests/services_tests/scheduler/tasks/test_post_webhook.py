from datetime import datetime, timedelta

from pydantic import UUID4

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.webhook import SaveWebhook, WebhookType
from mealie.services.event_bus_service.event_bus_listeners import WebhookEventListener
from tests.utils import random_string
from tests.utils.factories import random_bool
from tests.utils.fixture_schemas import TestUser


def webhook_factory(
    group_id: str | UUID4,
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
        scheduled_time=scheduled_time.time() if scheduled_time else datetime.now().time(),
        group_id=group_id,
    )


def test_get_scheduled_webhooks_filter_query(database: AllRepositories, unique_user: TestUser):
    """
    get_scheduled_webhooks_test tests the get_scheduled_webhooks function on the webhook event bus listener.
    """

    expected: list[SaveWebhook] = []

    start = datetime.now()

    for _ in range(5):
        new_item = webhook_factory(group_id=unique_user.group_id, enabled=random_bool())
        out_of_range_item = webhook_factory(
            group_id=unique_user.group_id,
            enabled=random_bool(),
            scheduled_time=(start - timedelta(minutes=20)),
        )

        database.webhooks.create(new_item)
        database.webhooks.create(out_of_range_item)

        if new_item.enabled:
            expected.append(new_item)

    event_bus_listener = WebhookEventListener(database.session, unique_user.group_id)  # type: ignore
    results = event_bus_listener.get_scheduled_webhooks(start, datetime.now() + timedelta(minutes=5))

    assert len(results) == len(expected)

    for result in results:
        assert result.enabled

        for expected_item in expected:

            if result.name == expected_item.name:  # Names are uniquely generated so we can use this to compare
                assert result.enabled == expected_item.enabled
                break
