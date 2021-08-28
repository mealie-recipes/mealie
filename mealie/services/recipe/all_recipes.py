import json
from functools import lru_cache

from fastapi import Depends, Response
from fastapi.encoders import jsonable_encoder
from mealie.core.root_logger import get_logger
from mealie.db.database import db
from mealie.db.db_setup import SessionLocal, generate_session
from mealie.routes.deps import is_logged_in
from mealie.schema.recipe import RecipeSummary
from sqlalchemy.orm.session import Session

logger = get_logger()


class AllRecipesService:
    def __init__(self, session: Session = Depends(generate_session), is_user: bool = Depends(is_logged_in)):
        self.start = 0
        self.limit = 9999
        self.session = session or SessionLocal()
        self.is_user = is_user

    @classmethod
    def query(
        cls, start=0, limit=9999, session: Session = Depends(generate_session), is_user: bool = Depends(is_logged_in)
    ):
        set_query = cls(session, is_user)

        set_query.start = start
        set_query.limit = limit

        return set_query

    def get_recipes(self):
        if self.is_user:
            return get_all_recipes_user(self.limit, self.start)

        else:
            return get_all_recipes_public(self.limit, self.start)


@lru_cache(maxsize=1)
def get_all_recipes_user(limit, start):
    with SessionLocal() as session:
        all_recipes: list[RecipeSummary] = db.recipes.get_all(
            session, limit=limit, start=start, order_by="date_updated", override_schema=RecipeSummary
        )
        all_recipes_json = [recipe.dict() for recipe in all_recipes]
        return Response(content=json.dumps(jsonable_encoder(all_recipes_json)), media_type="application/json")


@lru_cache(maxsize=1)
def get_all_recipes_public(limit, start):
    with SessionLocal() as session:
        all_recipes: list[RecipeSummary] = db.recipes.get_all_public(
            session, limit=limit, start=start, order_by="date_updated", override_schema=RecipeSummary
        )
        all_recipes_json = [recipe.dict() for recipe in all_recipes]
        return Response(content=json.dumps(jsonable_encoder(all_recipes_json)), media_type="application/json")


def clear_all_cache():
    get_all_recipes_user.cache_clear()
    get_all_recipes_public.cache_clear()
    logger.info("All Recipes Cache Cleared")


def subscripte_to_recipe_events():
    db.recipes.subscribe(clear_all_cache)
    logger.info("All Recipes Subscribed to Database Events")
