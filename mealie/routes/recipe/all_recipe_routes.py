from fastapi import APIRouter, Depends
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.schema.recipe import RecipeSummary
from mealie.services.recipe.all_recipes import AllRecipesService
from sqlalchemy.orm.session import Session

router = APIRouter()


@router.get("")
def get_recipe_summary(all_recipes_service: AllRecipesService.query = Depends()):
    """
    Returns key the recipe summary data for recipes in the database. You can perform
    slice operations to set the skip/end amounts for recipes. All recipes are sorted by the added date.

    **Query Parameters**
    - skip: The database entry to start at. (0 Indexed)
    - end: The number of entries to return.

    skip=2, end=10 will return entries

    """

    return all_recipes_service.get_recipes()


@router.get("/summary/untagged", response_model=list[RecipeSummary])
async def get_untagged_recipes(count: bool = False, session: Session = Depends(generate_session)):
    return db.recipes.count_untagged(session, count=count, override_schema=RecipeSummary)


@router.get("/summary/uncategorized", response_model=list[RecipeSummary])
async def get_uncategorized_recipes(count: bool = False, session: Session = Depends(generate_session)):
    return db.recipes.count_uncategorized(session, count=count, override_schema=RecipeSummary)
