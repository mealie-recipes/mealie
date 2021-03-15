import json
from datetime import date

import requests
from db.database import db
from db.db_setup import create_session
from schema.meal import MealOut, MealPlanInDB
from schema.user import GroupInDB
from sqlalchemy.orm.session import Session


def post_webhooks(group: int, session: Session = None):
    session = session if session else create_session()
    group_settings: GroupInDB = db.groups.get(session, group)

    if group_settings.webhook_enable:
        today_slug = None

        for mealplan in group_settings.mealplans:
            mealplan: MealPlanInDB
            for meal in mealplan.meals:
                meal: MealOut
                if meal.date == date.today():
                    today_slug = meal.slug
                    break

        if not today_slug:
            return

        todays_meal = db.recipes.get(session, today_slug)

        for url in group_settings.webhook_urls:
            requests.post(url, json=todays_meal.json())

    session.close()
