from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.schema.recipe import RecipeSummary

router = APIRouter()


@router.get("/summary/untagged", response_model=list[RecipeSummary])
async def get_untagged_recipes(count: bool = False, session: Session = Depends(generate_session)):
    return db.recipes.count_untagged(session, count=count, override_schema=RecipeSummary)


@router.get("/summary/uncategorized", response_model=list[RecipeSummary])
async def get_uncategorized_recipes(count: bool = False, session: Session = Depends(generate_session)):
    return db.recipes.count_uncategorized(session, count=count, override_schema=RecipeSummary)
