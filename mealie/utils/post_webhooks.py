import requests
from db.database import db
from db.db_setup import create_session
from schema.user import GroupInDB
from services.meal_services import get_todays_meal
from sqlalchemy.orm.session import Session


def post_webhooks(group: int, session: Session = None):
    session = session if session else create_session()
    group_settings: GroupInDB = db.groups.get(session, group)

    if not group_settings.webhook_enable:
        return 

    todays_recipe = get_todays_meal(session, group)

    if not todays_recipe:
        return

    for url in group_settings.webhook_urls:
        requests.post(url, json=todays_recipe.json())

    session.close()
