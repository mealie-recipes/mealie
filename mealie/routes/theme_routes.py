from fastapi import APIRouter, Depends, HTTPException, status
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.theme import SiteTheme
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api", tags=["Themes"])


@router.get("/themes")
def get_all_themes(session: Session = Depends(generate_session)):
    """ Returns all site themes """

    return db.themes.get_all(session)


@router.post("/themes/create", status_code=status.HTTP_201_CREATED)
def create_theme(data: SiteTheme, session: Session = Depends(generate_session), current_user=Depends(get_current_user)):
    """ Creates a site color theme database entry """
    db.themes.create(session, data.dict())


@router.get("/themes/{id}")
def get_single_theme(id: int, session: Session = Depends(generate_session)):
    """ Returns a named theme """
    return db.themes.get(session, id)


@router.put("/themes/{id}", status_code=status.HTTP_200_OK)
def update_theme(
    id: int,
    data: SiteTheme,
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):
    """ Update a theme database entry """
    db.themes.update(session, id, data.dict())


@router.delete("/themes/{id}", status_code=status.HTTP_200_OK)
def delete_theme(id: int, session: Session = Depends(generate_session), current_user=Depends(get_current_user)):
    """ Deletes theme from the database """
    try:
        db.themes.delete(session, id)
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
