import json

import requests
from db.database import db
from db.db_setup import create_session
from schema.settings import SiteSettings
from services.meal_services import get_todays_meal


def post_webhooks():
    session = create_session()
    all_settings = db.get(session, 1)
    all_settings = SiteSettings(**all_settings)

    if all_settings.webhooks.enabled:
        today_slug = get_todays_meal(session)
        todays_meal = db.recipes.get(session, today_slug)
        urls = all_settings.webhooks.webhookURLs

        for url in urls:
            requests.post(url, json.dumps(todays_meal, default=str))

    session.close()
