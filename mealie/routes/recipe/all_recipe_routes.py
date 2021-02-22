from typing import List, Optional

from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends, Query
from schema.recipe_models import AllRecipeRequest
from slugify import slugify
from sqlalchemy.orm.session import Session

router = APIRouter(tags=["Query All Recipes"])


@router.get("/api/recipes")
def get_all_recipes(
    keys: Optional[List[str]] = Query(...),
    num: Optional[int] = 100,
    session: Session = Depends(generate_session),
):
    """
    Returns key data for all recipes based off the query paramters provided.
    For example, if slug, image, and name are provided you will recieve a list of
    recipes containing the slug, image, and name property. By default, responses
    are limited to 100.

    At this time you can only query top level values:

    - slug
    - name
    - description
    - image
    - recipeYield
    - totalTime
    - prepTime
    - performTime
    - rating
    - orgURL

    **Note:** You may experience problems with with query parameters. As an alternative
    you may also use the post method and provide a body.
    See the *Post* method for more details.
    """

    return db.recipes.get_all_limit_columns(session, keys, limit=num)


@router.post("/api/recipes")
def get_all_recipes_post(
    body: AllRecipeRequest, session: Session = Depends(generate_session)
):
    """
    Returns key data for all recipes based off the body data provided.
    For example, if slug, image, and name are provided you will recieve a list of
    recipes containing the slug, image, and name property.

    At this time you can only query top level values:

    - slug
    - name
    - description
    - image
    - recipeYield
    - totalTime
    - prepTime
    - performTime
    - rating
    - orgURL

    Refer to the body example for data formats.

    """

    return db.recipes.get_all_limit_columns(session, body.properties, body.limit)


@router.post("/api/recipes/category")
def filter_by_category(categories: list, session: Session = Depends(generate_session)):
    """ pass a list of categories and get a list of recipes associated with those categories """
    #! This should be refactored into a single database call, but I couldn't figure it out
    in_category = [
        db.categories.get(session, slugify(cat), limit=1) for cat in categories
    ]
    in_category = [cat.get("recipes") for cat in in_category]
    in_category = [item for sublist in in_category for item in sublist]
    return in_category


@router.post("/api/recipes/tag")
async def filter_by_tags(tags: list, session: Session = Depends(generate_session)):
    """ pass a list of tags and get a list of recipes associated with those tags"""
    #! This should be refactored into a single database call, but I couldn't figure it out
    in_tags = [db.tags.get(session, slugify(tag), limit=1) for tag in tags]
    in_tags = [tag.get("recipes") for tag in in_tags]
    in_tags = [item for sublist in in_tags for item in sublist]
    return in_tags
