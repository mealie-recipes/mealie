from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from models.category_models import RecipeCategoryResponse
from sqlalchemy.orm.session import Session

router = APIRouter(
    prefix="/api/recipes/categories",
    tags=["Recipes"],
)


@router.get("/all/")
async def get_all_recipe_categories(session: Session = Depends(generate_session)):
    """ Returns a list of available categories in the database """

    return db.categories.get_all_primary_keys(session)


@router.get("/{category}/", response_model=RecipeCategoryResponse)
def get_all_recipes_by_category(
    category: str, session: Session = Depends(generate_session)
):
    """ Returns a list of recipes associated with the provided category. """
    return db.categories.get(session, category)
