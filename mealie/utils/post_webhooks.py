import json

import requests
from sqlalchemy.orm.session import Session

from mealie.db.database import get_database
from mealie.db.db_setup import create_session
from mealie.schema.user import GroupInDB
from mealie.services.events import create_scheduled_event


def post_webhooks(group: int, session: Session = None, force=True):
    session = session or create_session()
    db = get_database(session)
    group_settings: GroupInDB = db.groups.get(group)

    if not group_settings.webhook_enable and not force:
        return

    # TODO: Fix Mealplan Webhooks
    todays_recipe = None

    if not todays_recipe:
        return

    for url in group_settings.webhook_urls:
        requests.post(url, json=json.loads(todays_recipe.json(by_alias=True)))

        create_scheduled_event("Meal Plan Webhook", f"Meal plan webhook executed for group '{group}'")

    session.close()
