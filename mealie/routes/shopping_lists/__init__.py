from fastapi import Depends
from sqlalchemy.orm.session import Session

from mealie.core.dependencies import get_current_user
from mealie.db.db_setup import generate_session
from mealie.repos.all_repositories import get_repositories
from mealie.routes.routers import UserAPIRouter
from mealie.schema.meal_plan import ShoppingListIn, ShoppingListOut
from mealie.schema.user import PrivateUser

router = UserAPIRouter(prefix="/shopping-lists", tags=["Shopping Lists: CRUD"])


@router.post("", response_model=ShoppingListOut)
async def create_shopping_list(
    list_in: ShoppingListIn,
    current_user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """Create Shopping List in the Database"""
    db = get_repositories(session)
    list_in.group = current_user.group

    return db.shopping_lists.create(list_in)


@router.get("/{id}", response_model=ShoppingListOut)
async def get_shopping_list(id: int, session: Session = Depends(generate_session)):
    """Get Shopping List from the Database"""
    db = get_repositories(session)
    return db.shopping_lists.get(id)


@router.put("/{id}", response_model=ShoppingListOut)
async def update_shopping_list(id: int, new_data: ShoppingListIn, session: Session = Depends(generate_session)):
    """Update Shopping List in the Database"""
    db = get_repositories(session)
    return db.shopping_lists.update(id, new_data)


@router.delete("/{id}")
async def delete_shopping_list(id: int, session: Session = Depends(generate_session)):
    """Delete Shopping List from the Database"""
    db = get_repositories(session)
    return db.shopping_lists.delete(id)
