from fastapi import APIRouter, Depends, HTTPException, status
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import is_logged_in
from mealie.routes.routers import AdminAPIRouter, UserAPIRouter
from mealie.schema.category import RecipeTagResponse, TagIn
from sqlalchemy.orm.session import Session

public_router = APIRouter(prefix="/api/tags", tags=["Recipe Tags"])
user_router = UserAPIRouter(prefix="/api/tags", tags=["Recipe Tags"])
admin_router = AdminAPIRouter(prefix="/api/tags", tags=["Recipe Tags"])


@public_router.get("")
async def get_all_recipe_tags(session: Session = Depends(generate_session)):
    """ Returns a list of available tags in the database """
    return db.tags.get_all_limit_columns(session, ["slug", "name"])


@public_router.get("/empty")
def get_empty_tags(session: Session = Depends(generate_session)):
    """ Returns a list of tags that do not contain any recipes"""
    return db.tags.get_empty(session)


@public_router.get("/{tag}", response_model=RecipeTagResponse)
def get_all_recipes_by_tag(
    tag: str, session: Session = Depends(generate_session), is_user: bool = Depends(is_logged_in)
):
    """ Returns a list of recipes associated with the provided tag. """
    tag_obj = db.tags.get(session, tag)
    tag_obj = RecipeTagResponse.from_orm(tag_obj)

    if not is_user:
        tag_obj.recipes = [x for x in tag_obj.recipes if x.settings.public]

    return tag_obj


@user_router.post("")
async def create_recipe_tag(tag: TagIn, session: Session = Depends(generate_session)):
    """ Creates a Tag in the database """

    return db.tags.create(session, tag.dict())


@admin_router.put("/{tag}", response_model=RecipeTagResponse)
async def update_recipe_tag(tag: str, new_tag: TagIn, session: Session = Depends(generate_session)):
    """ Updates an existing Tag in the database """

    return db.tags.update(session, tag, new_tag.dict())


@admin_router.delete("/{tag}")
async def delete_recipe_tag(tag: str, session: Session = Depends(generate_session)):
    """Removes a recipe tag from the database. Deleting a
    tag does not impact a recipe. The tag will be removed
    from any recipes that contain it"""

    try:
        db.tags.delete(session, tag)
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
