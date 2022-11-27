from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from mealie.db.db_setup import generate_session
from mealie.repos.all_repositories import get_repositories
from mealie.schema.recipe import RecipeSummary
from mealie.schema.response.pagination import PaginationQuery

router = APIRouter()


@router.get("/summary/untagged", response_model=list[RecipeSummary])
async def get_untagged_recipes(count: bool = False, session: Session = Depends(generate_session)):
    db = get_repositories(session)
    return db.recipes.count_untagged(count=count, override_schema=RecipeSummary)


@router.get("/summary/uncategorized", response_model=list[RecipeSummary])
async def get_uncategorized_recipes(count: bool = False, session: Session = Depends(generate_session)):
    db = get_repositories(session)
    return db.recipes.count_uncategorized(count=count, override_schema=RecipeSummary)


@router.get("/summar/whatever")
async def get_whatever(session: Session = Depends(generate_session)):
    db = get_repositories(session)
    payload = db.tags.get_all_count_recipes(
        PaginationQuery(),
    )

    return payload
