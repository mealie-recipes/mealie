import json

import requests
from mealie.db.database import db
from mealie.db.db_setup import create_session
from mealie.schema.user import GroupInDB
from mealie.services.events import create_scheduled_event
from mealie.services.meal_services import get_todays_meal
from sqlalchemy.orm.session import Session


def post_webhooks(group: int, session: Session = None, force=True):
    session = session or create_session()
    group_settings: GroupInDB = db.groups.get(session, group)

    if not group_settings.webhook_enable and not force:
        return

    todays_recipe = get_todays_meal(session, group)

    if not todays_recipe:
        return

    for url in group_settings.webhook_urls:
        requests.post(url, json=json.loads(todays_recipe.json(by_alias=True)))

        create_scheduled_event("Meal Plan Webhook", f"Meal plan webhook executed for group '{group}'")

    session.close()
