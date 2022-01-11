from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from mealie.core.dependencies import is_logged_in
from mealie.db.db_setup import generate_session
from mealie.repos.all_repositories import get_repositories
from mealie.routes.routers import AdminAPIRouter, UserAPIRouter
from mealie.schema.recipe import RecipeTagResponse, TagIn

public_router = APIRouter()
user_router = UserAPIRouter()
admin_router = AdminAPIRouter()


@public_router.get("")
async def get_all_recipe_tags(session: Session = Depends(generate_session)):
    """Returns a list of available tags in the database"""
    db = get_repositories(session)
    return db.tags.get_all_limit_columns(["slug", "name"])


@public_router.get("/empty")
def get_empty_tags(session: Session = Depends(generate_session)):
    """Returns a list of tags that do not contain any recipes"""
    db = get_repositories(session)
    return db.tags.get_empty()


@public_router.get("/{tag}", response_model=RecipeTagResponse)
def get_all_recipes_by_tag(
    tag: str, session: Session = Depends(generate_session), is_user: bool = Depends(is_logged_in)
):
    """Returns a list of recipes associated with the provided tag."""
    db = get_repositories(session)
    tag_obj = db.tags.get(tag)
    tag_obj = RecipeTagResponse.from_orm(tag_obj)

    if not is_user:
        tag_obj.recipes = [x for x in tag_obj.recipes if x.settings.public]

    return tag_obj


@user_router.post("", status_code=201)
async def create_recipe_tag(tag: TagIn, session: Session = Depends(generate_session)):
    """Creates a Tag in the database"""
    db = get_repositories(session)
    return db.tags.create(tag.dict())


@user_router.put("/{tag}", response_model=RecipeTagResponse)
async def update_recipe_tag(tag: str, new_tag: TagIn, session: Session = Depends(generate_session)):
    """Updates an existing Tag in the database"""
    db = get_repositories(session)
    return db.tags.update(tag, new_tag.dict())


@user_router.delete("/{tag}")
async def delete_recipe_tag(tag: str, session: Session = Depends(generate_session)):
    """Removes a recipe tag from the database. Deleting a
    tag does not impact a recipe. The tag will be removed
    from any recipes that contain it"""

    try:
        db = get_repositories(session)
        db.tags.delete(tag)
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
