from fastapi import APIRouter, Depends
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.db.models.recipe.ingredient import IngredientModel
from mealie.db.models.recipe.nutrition import NutritionModel
from sqlalchemy.orm import Session
from mealie.db.session import get_db

from . import (
    admin,
    app,
    auth,
    comments,
    explore,
    groups,
    households,
    organizers,
    parser,
    recipe,
    shared,
    unit_and_foods,
    users,
    validators,
)

router = APIRouter(prefix="/api")

router.include_router(app.router)
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(households.router)
router.include_router(groups.router)
router.include_router(recipe.router)
router.include_router(organizers.router)
router.include_router(shared.router)
router.include_router(comments.router)
router.include_router(parser.router)
router.include_router(unit_and_foods.router)
router.include_router(admin.router)
router.include_router(validators.router)
router.include_router(explore.router)

router = APIRouter()

@router.post("/ingredients")
def create_ingredient(ingredient: RecipeIngredient, db: Session = Depends(get_db)):
    db_ingredient = IngredientModel(**ingredient.dict(exclude={"nutrition"}))
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)

    if ingredient.nutrition:
        db_nutrition = NutritionModel(
            ingredient_id=db_ingredient.id,
            **ingredient.nutrition.dict(exclude_unset=True)
        )
        db.add(db_nutrition)
        db.commit()

    return db_ingredient