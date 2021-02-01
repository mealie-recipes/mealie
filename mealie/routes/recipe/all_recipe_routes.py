from typing import List, Optional

from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends, Query
from models.recipe_models import AllRecipeRequest
from sqlalchemy.orm.session import Session

router = APIRouter(tags=["Recipes"])


@router.get("/api/all-recipes/")
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


@router.post("/api/all-recipes/")
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
