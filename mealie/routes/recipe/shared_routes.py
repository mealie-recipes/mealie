from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.orm.session import Session

from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.schema.recipe import Recipe

router = APIRouter()


@router.get("/shared/{recipe_slug}", response_model=Recipe)
def get_shared_recipe(share_key: UUID4, session: Session = Depends(generate_session)):
    _ = get_database(session)
    print("Shared Recipe -> ", share_key)
