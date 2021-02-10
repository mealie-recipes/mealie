import json

import requests
from db.database import db
from db.db_setup import create_session
from models.settings_models import SiteSettings
from services.meal_services import MealPlan
from services.recipe_services import Recipe


def post_webhooks():
    session = create_session()
    all_settings = db.get(session, "main")
    all_settings = SiteSettings(**all_settings)

    if all_settings.webhooks.enabled:
        todays_meal = Recipe.get_by_slug(MealPlan.today()).dict()
        urls = all_settings.webhooks.webhookURLs

        for url in urls:
            requests.post(url, json.dumps(todays_meal, default=str))

    session.close()
