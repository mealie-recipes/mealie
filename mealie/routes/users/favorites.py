from fastapi import Depends
from sqlalchemy.orm.session import Session

from mealie.core.dependencies import get_current_user
from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.user import PrivateUser, UserFavorites

user_router = UserAPIRouter()


@user_router.get("/{id}/favorites", response_model=UserFavorites)
async def get_favorites(id: str, session: Session = Depends(generate_session)):
    """ Get user's favorite recipes """
    db = get_database(session)
    return db.users.get(id, override_schema=UserFavorites)


@user_router.post("/{id}/favorites/{slug}")
def add_favorite(
    slug: str,
    current_user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Adds a Recipe to the users favorites """

    current_user.favorite_recipes.append(slug)
    db = get_database(session)
    db.users.update(current_user.id, current_user)


@user_router.delete("/{id}/favorites/{slug}")
def remove_favorite(
    slug: str,
    current_user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Adds a Recipe to the users favorites """

    assert_user_change_allowed(id, current_user)
    current_user.favorite_recipes = [x for x in current_user.favorite_recipes if x != slug]

    db = get_database(session)
    db.users.update(current_user.id, current_user)

    return
