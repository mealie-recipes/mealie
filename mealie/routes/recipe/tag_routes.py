from fastapi import APIRouter, Depends, HTTPException, status
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.category import RecipeTagResponse, TagIn
from sqlalchemy.orm.session import Session

router = APIRouter(tags=["Recipes"])

router = APIRouter(prefix="/api/tags", tags=["Recipe Tags"])


@router.get("")
async def get_all_recipe_tags(session: Session = Depends(generate_session)):
    """ Returns a list of available tags in the database """
    return db.tags.get_all_limit_columns(session, ["slug", "name"])


@router.get("/empty")
def get_empty_tags(session: Session = Depends(generate_session)):
    """ Returns a list of tags that do not contain any recipes"""
    return db.tags.get_empty(session)


@router.get("/{tag}", response_model=RecipeTagResponse)
def get_all_recipes_by_tag(tag: str, session: Session = Depends(generate_session)):
    """ Returns a list of recipes associated with the provided tag. """
    return db.tags.get(session, tag)


@router.post("")
async def create_recipe_tag(
    tag: TagIn, session: Session = Depends(generate_session), current_user=Depends(get_current_user)
):
    """ Creates a Tag in the database """

    return db.tags.create(session, tag.dict())


@router.put("/{tag}", response_model=RecipeTagResponse)
async def update_recipe_tag(
    tag: str, new_tag: TagIn, session: Session = Depends(generate_session), current_user=Depends(get_current_user)
):
    """ Updates an existing Tag in the database """

    return db.tags.update(session, tag, new_tag.dict())


@router.delete("/{tag}")
async def delete_recipe_tag(
    tag: str, session: Session = Depends(generate_session), current_user=Depends(get_current_user)
):
    """Removes a recipe tag from the database. Deleting a
    tag does not impact a recipe. The tag will be removed
    from any recipes that contain it"""

    try:
        db.tags.delete(session, tag)
    except:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
