from fastapi import Depends
from sqlalchemy.orm.session import Session

from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.core.dependencies import get_current_user
from mealie.routes.routers import UserAPIRouter
from mealie.schema.meal_plan import ShoppingListIn, ShoppingListOut
from mealie.schema.user import UserInDB

router = UserAPIRouter(prefix="/shopping-lists", tags=["Shopping Lists: CRUD"])


@router.post("", response_model=ShoppingListOut)
async def create_shopping_list(
    list_in: ShoppingListIn,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Create Shopping List in the Database """

    list_in.group = current_user.group

    return db.shopping_lists.create(session, list_in)


@router.get("/{id}", response_model=ShoppingListOut)
async def get_shopping_list(id: int, session: Session = Depends(generate_session)):
    """ Get Shopping List from the Database """
    return db.shopping_lists.get(session, id)


@router.put("/{id}", response_model=ShoppingListOut)
async def update_shopping_list(id: int, new_data: ShoppingListIn, session: Session = Depends(generate_session)):
    """ Update Shopping List in the Database """
    return db.shopping_lists.update(session, id, new_data)


@router.delete("/{id}")
async def delete_shopping_list(id: int, session: Session = Depends(generate_session)):
    """ Delete Shopping List from the Database """
    return db.shopping_lists.delete(session, id)
