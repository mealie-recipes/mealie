from typing import Union

from fastapi import APIRouter, Depends
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_admin_user
from mealie.schema.settings import CustomPageBase, CustomPageOut
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/site-settings/custom-pages", tags=["Settings"])


@router.get("")
def get_custom_pages(session: Session = Depends(generate_session)):
    """ Returns the sites custom pages """

    return db.custom_pages.get_all(session)


@router.post("", dependencies=[Depends(get_admin_user)])
async def create_new_page(
    new_page: CustomPageBase,
    session: Session = Depends(generate_session),
):
    """ Creates a new Custom Page """

    db.custom_pages.create(session, new_page.dict())


@router.put("", dependencies=[Depends(get_admin_user)])
async def update_multiple_pages(pages: list[CustomPageOut], session: Session = Depends(generate_session)):
    """ Update multiple custom pages """
    for page in pages:
        db.custom_pages.update(session, page.id, page.dict())


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


@router.put("/{id}", dependencies=[Depends(get_admin_user)])
async def update_single_page(
    data: CustomPageOut,
    id: int,
    session: Session = Depends(generate_session),
):
    """ Removes a custom page from the database """

    return db.custom_pages.update(session, id, data.dict())


@router.delete("/{id}", dependencies=[Depends(get_admin_user)])
async def delete_custom_page(
    id: int,
    session: Session = Depends(generate_session),
):
    """ Removes a custom page from the database """

    db.custom_pages.delete(session, id)
    return
