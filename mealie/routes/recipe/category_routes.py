from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from models.category_models import RecipeCategoryResponse
from sqlalchemy.orm.session import Session

router = APIRouter(
    prefix="/api/categories",
    tags=["Recipe Categories"],
)


@router.get("")
async def get_all_recipe_categories(session: Session = Depends(generate_session)):
    """ Returns a list of available categories in the database """
    return db.categories.get_all_limit_columns(session, ["slug", "name"])


@router.get("/{category}", response_model=RecipeCategoryResponse)
def get_all_recipes_by_category(
    category: str, session: Session = Depends(generate_session)
):
    """ Returns a list of recipes associated with the provided category. """
    return db.categories.get(session, category)


@router.delete("/{category}")
async def delete_recipe_category(
    category: str, session: Session = Depends(generate_session)
):
    """ Removes a recipe category from the database. Deleting a 
    category does not impact a recipe. The category will be removed
    from any recipes that contain it """

    db.categories.delete(session, category)
