from fastapi import APIRouter, Depends, status, HTTPException
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



@router.get("/themes/{theme_name}")
def get_single_theme(theme_name: str, session: Session = Depends(generate_session)):
    """ Returns a named theme """
    return db.themes.get(session, theme_name)


@router.put("/themes/{theme_name}", status_code=status.HTTP_200_OK)
def update_theme(
    theme_name: str,
    data: SiteTheme,
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):
    """ Update a theme database entry """
    db.themes.update(session, theme_name, data.dict())


@router.delete("/themes/{theme_name}", status_code=status.HTTP_200_OK)
def delete_theme(theme_name: str, session: Session = Depends(generate_session), current_user=Depends(get_current_user)):
    """ Deletes theme from the database """
    try:
        db.themes.delete(session, theme_name)
    except:
        raise HTTPException( status.HTTP_400_BAD_REQUEST )
