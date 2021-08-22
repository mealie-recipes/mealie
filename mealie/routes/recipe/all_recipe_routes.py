from fastapi import APIRouter, Depends
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import is_logged_in
from mealie.schema.recipe import RecipeSummary
from mealie.services.recipe.all_recipes import get_all_recipes_public, get_all_recipes_user
from sqlalchemy.orm.session import Session

router = APIRouter()


@router.get("")
def get_recipe_summary(start=0, limit=9999, user: bool = Depends(is_logged_in)):
    """
    Returns key the recipe summary data for recipes in the database. You can perform
    slice operations to set the skip/end amounts for recipes. All recipes are sorted by the added date.

    **Query Parameters**
    - skip: The database entry to start at. (0 Indexed)
    - end: The number of entries to return.

    skip=2, end=10 will return entries

    """

    if user:
        return get_all_recipes_user(limit, start)

    else:
        return get_all_recipes_public(limit, start)


@router.get("/summary/untagged", response_model=list[RecipeSummary])
async def get_untagged_recipes(count: bool = False, session: Session = Depends(generate_session)):
    return db.recipes.count_untagged(session, count=count, override_schema=RecipeSummary)


@router.get("/summary/uncategorized", response_model=list[RecipeSummary])
async def get_uncategorized_recipes(count: bool = False, session: Session = Depends(generate_session)):
    return db.recipes.count_uncategorized(session, count=count, override_schema=RecipeSummary)
