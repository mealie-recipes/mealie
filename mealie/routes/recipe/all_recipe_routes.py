from typing import List, Optional

from db.db_setup import generate_session
from fastapi import APIRouter, Depends, Query
from models.recipe_models import AllRecipeRequest
from services.recipe_services import read_requested_values
from sqlalchemy.orm.session import Session

router = APIRouter(tags=["Recipes"])


@router.get("/api/all-recipes/", response_model=List[dict])
def get_all_recipes(
    keys: Optional[List[str]] = Query(...),
    num: Optional[int] = 100,
    db: Session = Depends(generate_session),
):
    """
    Returns key data for all recipes based off the query paramters provided.
    For example, if slug, image, and name are provided you will recieve a list of
    recipes containing the slug, image, and name property. By default, responses
    are limited to 100.

    **Note:** You may experience problems with with query parameters. As an alternative
    you may also use the post method and provide a body.
    See the *Post* method for more details.
    """

    all_recipes = read_requested_values(db, keys, num)
    return all_recipes


@router.post("/api/all-recipes/", response_model=List[dict])
def get_all_recipes_post(
    body: AllRecipeRequest, db: Session = Depends(generate_session)
):
    """
    Returns key data for all recipes based off the body data provided.
    For example, if slug, image, and name are provided you will recieve a list of
    recipes containing the slug, image, and name property.

    Refer to the body example for data formats.

    """

    all_recipes = read_requested_values(db, body.properties, body.limit)

    return all_recipes
