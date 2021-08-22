from fastapi import Depends, status
from mealie.db.database import db
from mealie.db.db_setup import Session, generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.recipe.units_and_foods import CreateIngredientUnit, IngredientUnit

router = UserAPIRouter()


@router.get("", response_model=list[IngredientUnit])
async def get_all(
    session: Session = Depends(generate_session),
):
    """ Get unit from the Database """
    # Get unit
    return db.ingredient_units.get_all(session)


@router.post("", response_model=IngredientUnit, status_code=status.HTTP_201_CREATED)
async def create_unit(unit: CreateIngredientUnit, session: Session = Depends(generate_session)):
    """ Create unit in the Database """

    return db.ingredient_units.create(session, unit)


@router.get("/{id}")
async def get_unit(id: str, session: Session = Depends(generate_session)):
    """ Get unit from the Database """

    return db.ingredient_units.get(session, id)


@router.put("/{id}")
async def update_unit(id: str, unit: CreateIngredientUnit, session: Session = Depends(generate_session)):
    """ Update unit in the Database """

    return db.ingredient_units.update(session, id, unit)


@router.delete("/{id}")
async def delete_unit(id: str, session: Session = Depends(generate_session)):
    """ Delete unit from the Database """
    return db.ingredient_units.delete(session, id)
