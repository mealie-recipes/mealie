from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.routers import AdminAPIRouter
from mealie.schema.admin import CustomPageBase, CustomPageOut

public_router = APIRouter(prefix="/api/site-settings/custom-pages", tags=["Settings"])
admin_router = AdminAPIRouter(prefix="/api/site-settings/custom-pages", tags=["Settings"])


@public_router.get("")
def get_custom_pages(session: Session = Depends(generate_session)):
    """ Returns the sites custom pages """

    return db.custom_pages.get_all(session)


@admin_router.post("")
async def create_new_page(
    new_page: CustomPageBase,
    session: Session = Depends(generate_session),
):
    """ Creates a new Custom Page """

    db.custom_pages.create(session, new_page.dict())


@admin_router.put("")
async def update_multiple_pages(pages: list[CustomPageOut], session: Session = Depends(generate_session)):
    """ Update multiple custom pages """
    for page in pages:
        db.custom_pages.update(session, page.id, page.dict())


@public_router.get("/{id}")
async def get_single_page(
    id: Union[int, str],
    session: Session = Depends(generate_session),
):
    """ Removes a custom page from the database """
    if isinstance(id, int):
        return db.custom_pages.get(session, id)
    elif isinstance(id, str):
        return db.custom_pages.get(session, id, "slug")


@admin_router.put("/{id}")
async def update_single_page(
    data: CustomPageOut,
    id: int,
    session: Session = Depends(generate_session),
):
    """ Removes a custom page from the database """

    return db.custom_pages.update(session, id, data.dict())


@admin_router.delete("/{id}")
async def delete_custom_page(
    id: int,
    session: Session = Depends(generate_session),
):
    """ Removes a custom page from the database """

    db.custom_pages.delete(session, id)
    return
