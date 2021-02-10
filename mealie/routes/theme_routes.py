from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from services.settings_services import SiteTheme
from sqlalchemy.orm.session import Session
from utils.snackbar import SnackResponse

router = APIRouter(prefix="/api", tags=["Themes"])


@router.get("/themes")
def get_all_themes(session: Session = Depends(generate_session)):
    """ Returns all site themes """

    return SiteTheme.get_all(session)


@router.post("/themes/create")
def create_theme(data: SiteTheme, session: Session = Depends(generate_session)):
    """ Creates a site color theme database entry """
    data.save_to_db(session)

    return SnackResponse.success("Theme Saved")


@router.get("/themes/{theme_name}")
def get_single_theme(theme_name: str, session: Session = Depends(generate_session)):
    """ Returns a named theme """
    return SiteTheme.get_by_name(session, theme_name)


@router.put("/themes/{theme_name}")
def update_theme(
    theme_name: str, data: SiteTheme, session: Session = Depends(generate_session)
):
    """ Update a theme database entry """
    data.update_document(session)

    return SnackResponse.info(f"Theme Updated: {theme_name}")


@router.delete("/themes/{theme_name}")
def delete_theme(theme_name: str, session: Session = Depends(generate_session)):
    """ Deletes theme from the database """
    SiteTheme.delete_theme(session, theme_name)

    return SnackResponse.error(f"Theme Deleted: {theme_name}")
