from typing import Union

from fastapi import APIRouter, Depends
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.settings import CustomPageBase, CustomPageOut
from mealie.schema.snackbar import SnackResponse
from mealie.schema.user import UserInDB
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/site-settings/custom-pages", tags=["Settings"])


@router.get("")
def get_custom_pages(session: Session = Depends(generate_session)):
    """ Returns the sites custom pages """

    return db.custom_pages.get_all(session)


@router.post("")
async def create_new_page(
    new_page: CustomPageBase,
    session: Session = Depends(generate_session),
    current_user: UserInDB = Depends(get_current_user),
):
    """ Creates a new Custom Page """

    db.custom_pages.create(session, new_page.dict())

    return SnackResponse.success("New Page Created")


@router.put("")
async def update_multiple_pages(
    pages: list[CustomPageOut],
    session: Session = Depends(generate_session),
    current_user: UserInDB = Depends(get_current_user),
):
    """ Update multiple custom pages """
    for page in pages:
        db.custom_pages.update(session, page.id, page.dict())
    return SnackResponse.success("Pages Updated")


@router.get("/{id}")
async def get_single_page(
    id: Union[int, str],
    session: Session = Depends(generate_session),
):
    """ Removes a custom page from the database """
    if isinstance(id, int):
        return db.custom_pages.get(session, id)
    elif isinstance(id, str):
        return db.custom_pages.get(session, id, "slug")


@router.put("/{id}")
async def update_single_age(
    data: CustomPageOut,
    id: int,
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):
    """ Removes a custom page from the database """

    return db.custom_pages.update(session, id, data.dict())


@router.delete("/{id}")
async def delete_custom_page(
    id: int,
    session: Session = Depends(generate_session),
    current_user: UserInDB = Depends(get_current_user),
):
    """ Removes a custom page from the database """

    db.custom_pages.delete(session, id)
    return
