import json
from functools import lru_cache

from fastapi import Response
from fastapi.encoders import jsonable_encoder
from mealie.core.root_logger import get_logger
from mealie.db.database import db
from mealie.db.db_setup import SessionLocal
from mealie.schema.recipe import RecipeSummary

logger = get_logger()


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
