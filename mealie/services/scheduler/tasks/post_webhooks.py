from datetime import datetime, timedelta

import requests
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from mealie.core import root_logger
from mealie.db.db_setup import create_session
from mealie.db.models.group.webhooks import GroupWebhooksModel

last_ran = datetime.now()


def get_scheduled_webhooks(session: Session, bottom: datetime, top: datetime) -> list[GroupWebhooksModel]:
    """
    get_scheduled_webhooks queries the database for all webhooks scheduled between the bottom and
    top time ranges. It returns a list of GroupWebhooksModel objects.
    """

    return (
        session.query(GroupWebhooksModel)
        .where(
            GroupWebhooksModel.enabled == True,  # noqa: E712 - required for SQLAlchemy comparison
            GroupWebhooksModel.scheduled_time >= bottom.time(),
            GroupWebhooksModel.scheduled_time <= top.time(),
        )
        .all()
    )


def post_webhooks() -> None:
    global last_ran
    session = create_session()

    logger = root_logger.get_logger()
    results = get_scheduled_webhooks(session, last_ran, datetime.now() + timedelta(minutes=5))
    last_ran = datetime.now()

    for result in results:
        logger.debug(f"posting webhooks for entry {result}")
        requests.post(result.url, jsonable_encoder({}))  # TODO: add data to webhook
