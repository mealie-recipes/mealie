from fastapi import APIRouter, Depends, HTTPException, status
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import is_logged_in
from mealie.routes.routers import AdminAPIRouter, UserAPIRouter
from mealie.schema.category import CategoryIn, RecipeCategoryResponse
from sqlalchemy.orm.session import Session

public_router = APIRouter(prefix="/api/categories", tags=["Recipe Categories"])
user_router = UserAPIRouter(prefix="/api/categories", tags=["Recipe Categories"])
admin_router = AdminAPIRouter(prefix="/api/categories", tags=["Recipe Categories"])


@public_router.get("")
async def get_all_recipe_categories(session: Session = Depends(generate_session)):
    """ Returns a list of available categories in the database """
    return db.categories.get_all_limit_columns(session, ["slug", "name"])


@public_router.get("/empty")
def get_empty_categories(session: Session = Depends(generate_session)):
    """ Returns a list of categories that do not contain any recipes"""
    return db.categories.get_empty(session)


@public_router.get("/{category}", response_model=RecipeCategoryResponse)
def get_all_recipes_by_category(
    category: str, session: Session = Depends(generate_session), is_user: bool = Depends(is_logged_in)
):
    """ Returns a list of recipes associated with the provided category. """

    category_obj = db.categories.get(session, category)
    category_obj = RecipeCategoryResponse.from_orm(category_obj)

    if not is_user:
        category_obj.recipes = [x for x in category_obj.recipes if x.settings.public]

    return category_obj


@user_router.post("")
async def create_recipe_category(category: CategoryIn, session: Session = Depends(generate_session)):
    """ Creates a Category in the database """

    try:
        return db.categories.create(session, category.dict())
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


@admin_router.put("/{category}", response_model=RecipeCategoryResponse)
async def update_recipe_category(category: str, new_category: CategoryIn, session: Session = Depends(generate_session)):
    """ Updates an existing Tag in the database """

    try:
        return db.categories.update(session, category, new_category.dict())
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


@admin_router.delete("/{category}")
async def delete_recipe_category(category: str, session: Session = Depends(generate_session)):
    """
    Removes a recipe category from the database. Deleting a
    category does not impact a recipe. The category will be removed
    from any recipes that contain it
    """

    try:
        db.categories.delete(session, category)
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
