from datetime import datetime, timezone
from typing import Optional

from pydantic import UUID4

from mealie.db.db_setup import create_session
from mealie.repos.all_repositories import get_repositories
from mealie.services.event_bus_service.event_bus_service import EventBusService
from mealie.services.event_bus_service.event_types import (
    INTERNAL_INTEGRATION_ID,
    EventDocumentType,
    EventOperation,
    EventTypes,
    EventWebhookData,
)

last_ran = datetime.now(timezone.utc)


def post_group_webhooks(start_dt: Optional[datetime] = None, group_id: Optional[UUID4] = None) -> None:
    """Post webhook events to specified group, or all groups"""

    global last_ran

    end_dt = datetime.now(timezone.utc)
    if start_dt is None:
        # set the webhook query bounds to start at the last time the service ran
        start_dt = last_ran

    # update the last ran time so we continue here next time the service runs
    last_ran = end_dt

    if group_id is None:
        # publish the webhook event to each group's event bus
        session = create_session()
        repos = get_repositories(session)
        groups = repos.groups.get_all()
        group_ids = [group.id for group in groups]

    else:
        group_ids = [group_id]

    """
    At this time only mealplan webhooks are supported. To add support for more types,
    add a dispatch event for that type here (e.g. EventDocumentType.recipe_bulk_report) and
    handle the webhook data in the webhook event bus listener
    """

    event_type = EventTypes.webhook_task
    event_document_data = EventWebhookData(
        document_type=EventDocumentType.mealplan,
        operation=EventOperation.info,
        webhook_start_dt=start_dt,
        webhook_end_dt=end_dt,
    )

    for group_id in group_ids:
        event_bus = EventBusService(group_id=group_id)
        event_bus.dispatch(
            integration_id=INTERNAL_INTEGRATION_ID,
            group_id=group_id,
            event_type=event_type,
            document_data=event_document_data,
        )
