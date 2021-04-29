from fastapi import APIRouter, Depends, HTTPException, status
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.category import CategoryIn, RecipeCategoryResponse
from sqlalchemy.orm.session import Session

router = APIRouter(
    prefix="/api/categories",
    tags=["Recipe Categories"],
)


@router.get("")
async def get_all_recipe_categories(session: Session = Depends(generate_session)):
    """ Returns a list of available categories in the database """
    return db.categories.get_all_limit_columns(session, ["slug", "name"])


@router.get("/empty")
def get_empty_categories(session: Session = Depends(generate_session)):
    """ Returns a list of categories that do not contain any recipes"""
    return db.categories.get_empty(session)


@router.get("/{category}", response_model=RecipeCategoryResponse)
def get_all_recipes_by_category(category: str, session: Session = Depends(generate_session)):
    """ Returns a list of recipes associated with the provided category. """
    return db.categories.get(session, category)


@router.post("")
async def create_recipe_category(
    category: CategoryIn, session: Session = Depends(generate_session), current_user=Depends(get_current_user)
):
    """ Creates a Category in the database """

    try:
        return db.categories.create(session, category.dict())
    except:
        raise HTTPException( status.HTTP_400_BAD_REQUEST )


@router.put("/{category}", response_model=RecipeCategoryResponse)
async def update_recipe_category(
    category: str,
    new_category: CategoryIn,
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):
    """ Updates an existing Tag in the database """

    try:
        return db.categories.update(session, category, new_category.dict())
    except:
        raise HTTPException( status.HTTP_400_BAD_REQUEST )


@router.delete("/{category}")
async def delete_recipe_category(
    category: str, session: Session = Depends(generate_session), current_user=Depends(get_current_user)
):
    """Removes a recipe category from the database. Deleting a
    category does not impact a recipe. The category will be removed
    from any recipes that contain it"""

    try:
        db.categories.delete(session, category)
    except:
        raise HTTPException( status.HTTP_400_BAD_REQUEST )
