from datetime import datetime, timezone

import requests
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.db.db_setup import create_session
from mealie.db.models.group.webhooks import GroupWebhooksModel
from mealie.repos.all_repositories import get_repositories

last_ran = datetime.now(timezone.utc)


def get_scheduled_webhooks(session: Session, bottom: datetime, top: datetime) -> list[GroupWebhooksModel]:
    """
    get_scheduled_webhooks queries the database for all webhooks scheduled between the bottom and
    top time ranges. It returns a list of GroupWebhooksModel objects.
    """

    return (
        session.query(GroupWebhooksModel)
        .where(
            GroupWebhooksModel.enabled == True,  # noqa: E712 - required for SQLAlchemy comparison
            GroupWebhooksModel.scheduled_time > bottom.astimezone(timezone.utc).time(),
            GroupWebhooksModel.scheduled_time <= top.astimezone(timezone.utc).time(),
        )
        .all()
    )


def post_group_webhooks() -> None:
    global last_ran
    session = create_session()
    results = get_scheduled_webhooks(session, last_ran, datetime.now())

    last_ran = datetime.now(timezone.utc)

    repos = get_repositories(session)

    memo = {}

    def get_meals(group_id: UUID4):
        if group_id not in memo:
            memo[group_id] = repos.meals.get_all(group_id=group_id)
        return memo[group_id]

    for result in results:
        meals = get_meals(result.group_id)

        if not meals:
            continue

        requests.post(result.url, json=jsonable_encoder(meals))
