from fastapi import APIRouter, Depends
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.category import RecipeTagResponse, TagIn
from mealie.schema.snackbar import SnackResponse
from sqlalchemy.orm.session import Session

router = APIRouter(tags=["Recipes"])

router = APIRouter(
    prefix="/api/tags",
    tags=["Recipe Tags"],
)


@router.get("")
async def get_all_recipe_tags(session: Session = Depends(generate_session)):
    """ Returns a list of available tags in the database """
    return db.tags.get_all_limit_columns(session, ["slug", "name"])


@router.post("")
async def create_recipe_tag(
    tag: TagIn, session: Session = Depends(generate_session), current_user=Depends(get_current_user)
):
    """ Creates a Tag in the database """

    return db.tags.create(session, tag.dict())


@router.get("/{tag}", response_model=RecipeTagResponse)
def get_all_recipes_by_tag(tag: str, session: Session = Depends(generate_session)):
    """ Returns a list of recipes associated with the provided tag. """
    return db.tags.get(session, tag)


@router.delete("/{tag}")
async def delete_recipe_tag(
    tag: str, session: Session = Depends(generate_session), current_user=Depends(get_current_user)
):
    """Removes a recipe tag from the database. Deleting a
    tag does not impact a recipe. The tag will be removed
    from any recipes that contain it"""

    db.tags.delete(session, tag)

    return SnackResponse.error(f"Tag Deleted: {tag}")
