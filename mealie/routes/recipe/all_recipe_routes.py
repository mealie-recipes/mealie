from fastapi import APIRouter, Depends
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import is_user
from mealie.schema.recipe import RecipeSummary
from slugify import slugify
from sqlalchemy.orm.session import Session

router = APIRouter(tags=["Query All Recipes"])


@router.get("/api/recipes/summary", response_model=list[RecipeSummary])
async def get_recipe_summary(
    start=0, limit=9999, session: Session = Depends(generate_session), is_user: bool = Depends(is_user)
):
    """
    Returns key the recipe summary data for recipes in the database. You can perform
    slice operations to set the skip/end amounts for recipes. All recipes are sorted by the added date.

    **Query Parameters**
    - skip: The database entry to start at. (0 Indexed)
    - end: The number of entries to return.

    skip=2, end=10 will return entries

    """

    if is_user:
        return db.recipes.get_all(
            session, limit=limit, start=start, order_by="date_updated", override_schema=RecipeSummary
        )

    else:
        return db.recipes.get_all_not_private(
            session, limit=limit, start=start, order_by="date_updated", override_schema=RecipeSummary
        )


@router.get("/api/recipes/summary/untagged", response_model=list[RecipeSummary])
async def get_untagged_recipes(count: bool = False, session: Session = Depends(generate_session)):
    return db.recipes.count_untagged(session, count=count, override_schema=RecipeSummary)


@router.get("/api/recipes/summary/uncategorized", response_model=list[RecipeSummary])
async def get_uncategorized_recipes(count: bool = False, session: Session = Depends(generate_session)):
    return db.recipes.count_uncategorized(session, count=count, override_schema=RecipeSummary)


@router.post("/api/recipes/category")
def filter_by_category(categories: list, session: Session = Depends(generate_session)):
    """ pass a list of categories and get a list of recipes associated with those categories """
    # ! This should be refactored into a single database call, but I couldn't figure it out
    in_category = [db.categories.get(session, slugify(cat), limit=1) for cat in categories]
    in_category = [cat.recipes for cat in in_category if cat]
    in_category = [item for sublist in in_category for item in sublist]
    return in_category


@router.post("/api/recipes/tag")
async def filter_by_tags(tags: list, session: Session = Depends(generate_session)):
    """ pass a list of tags and get a list of recipes associated with those tags"""
    # ! This should be refactored into a single database call, but I couldn't figure it out
    in_tags = [db.tags.get(session, slugify(tag), limit=1) for tag in tags]
    in_tags = [tag.recipes for tag in in_tags]
    in_tags = [item for sublist in in_tags for item in sublist]
    return in_tags
