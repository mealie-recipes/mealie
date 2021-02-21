from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session
from utils.snackbar import SnackResponse

from utils.snackbar import SnackResponse

router = APIRouter(tags=["Recipes"])

router = APIRouter(
    prefix="/api/recipes/tags",
    tags=["Recipe Tags"],
)


@router.get("/")
async def get_all_recipe_tags(session: Session = Depends(generate_session)):
    """ Returns a list of available tags in the database """
    return db.tags.get_all_primary_keys(session)


@router.get("/{tag}")
def get_all_recipes_by_tag(tag: str, session: Session = Depends(generate_session)):
    """ Returns a list of recipes associated with the provided tag. """
    return db.tags.get(session, tag)


@router.delete("/{tag}")
async def delete_recipe_tag(tag: str, session: Session = Depends(generate_session)):
    """Removes a recipe tag from the database. Deleting a
    tag does not impact a recipe. The tag will be removed
    from any recipes that contain it"""

    db.tags.delete(session, tag)

    return SnackResponse.error(f"Tag Deleted: {tag}")
