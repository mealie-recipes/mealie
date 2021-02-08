import json

import requests
from db.db_setup import create_session
from services.meal_services import MealPlan
from services.recipe_services import Recipe
from services.settings_services import SiteSettings


def post_webhooks():
    session = create_session()
    all_settings = SiteSettings.get_site_settings(session)

    if all_settings.webhooks.enabled:
        todays_meal = Recipe.get_by_slug(MealPlan.today()).dict()
        urls = all_settings.webhooks.webhookURLs

        for url in urls:
            requests.post(url, json.dumps(todays_meal, default=str))

    session.close()
