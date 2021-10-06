import json

import requests
from sqlalchemy.orm.session import Session

from mealie.core import root_logger
from mealie.db.database import get_database
from mealie.db.db_setup import create_session
from mealie.schema.group.webhook import ReadWebhook

from ..scheduled_func import Cron, ScheduledFunc
from ..scheduler_service import SchedulerService

logger = root_logger.get_logger()


def post_webhooks(webhook_id: int, session: Session = None):
    session = session or create_session()
    db = get_database(session)
    webhook: ReadWebhook = db.webhooks.get_one(webhook_id)

    if not webhook.enabled:
        logger.info(f"Skipping webhook {webhook_id}. reasons: is disabled")
        return

    todays_recipe = db.meals.get_today(webhook.group_id)

    if not todays_recipe:
        return

    payload = json.loads([x.json(by_alias=True) for x in todays_recipe])
    response = requests.post(webhook.url, json=payload)

    if response.status_code != 200:
        logger.error(f"Error posting webhook to {webhook.url} ({response.status_code})")

    session.close()


def update_group_webhooks():
    session = create_session()
    db = get_database(session)

    webhooks: list[ReadWebhook] = db.webhooks.get_all()

    for webhook in webhooks:
        cron = Cron.parse(webhook.time)

        job_func = ScheduledFunc(
            id=webhook.id,
            name=f"Group {webhook.group_id} webhook",
            callback=post_webhooks,
            hour=cron.hours,
            minute=cron.minutes,
            args=(webhook.id),
        )

        SchedulerService.add_cron_job(job_func)
