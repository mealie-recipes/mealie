from fastapi import APIRouter, Depends
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.meal import MealPlanInDB
from mealie.schema.recipe import Recipe
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/meal-plans", tags=["Meal Plan"])


@router.get("/{id}/shopping-list")
def get_shopping_list(
    id: str,
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):

    #! Refactor into Single Database Call
    mealplan = db.meals.get(session, id)
    mealplan: MealPlanInDB
    slugs = [x.slug for x in mealplan.meals]
    recipes: list[Recipe] = [db.recipes.get(session, x) for x in slugs]
    return [{"name": x.name, "recipeIngredient": x.recipeIngredient} for x in recipes if x]
