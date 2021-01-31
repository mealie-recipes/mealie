from typing import List

from db.database import db


def get_all_categories(session) -> List[str]:
    categories = db.categories.get_all_primary_keys(session)

    return categories


def get_recipes_by_category(session):
    pass
