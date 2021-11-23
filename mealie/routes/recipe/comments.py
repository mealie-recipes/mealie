from fastapi import Depends
from sqlalchemy.orm.session import Session

from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.recipe.recipe_comments import RecipeCommentOut

router = UserAPIRouter()


@router.get("/{slug}/comments", response_model=list[RecipeCommentOut])
async def get_recipe_comments(
    slug: str,
    session: Session = Depends(generate_session),
):
    """Get all comments for a recipe"""
    db = get_database(session)
    recipe = db.recipes.get_one(slug)
    return db.comments.multi_query({"recipe_id": recipe.id})
