from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from services.settings_services import SiteTheme
from sqlalchemy.orm.session import Session
from utils.snackbar import SnackResponse

router = APIRouter(prefix="/api", tags=["Themes"])


@router.get("/themes")
def get_all_themes(db: Session = Depends(generate_session)):
    """ Returns all site themes """

    return SiteTheme.get_all(db)


@router.post("/themes/create")
def create_theme(data: SiteTheme, db: Session = Depends(generate_session)):
    """ Creates a site color theme database entry """
    data.save_to_db(db)
    # try:
    #     data.save_to_db()
    # except:
    #     raise HTTPException(
    #         status_code=400, detail=SnackResponse.error("Unable to Save Theme")
    #     )

    return SnackResponse.success("Theme Saved")


@router.get("/themes/{theme_name}")
def get_single_theme(theme_name: str, db: Session = Depends(generate_session)):
    """ Returns a named theme """
    return SiteTheme.get_by_name(db, theme_name)


@router.put("/themes/{theme_name}")
def update_theme(
    theme_name: str, data: SiteTheme, db: Session = Depends(generate_session)
):
    """ Update a theme database entry """
    data.update_document(db)

    # try:
    # except:
    #     raise HTTPException(
    #         status_code=400, detail=SnackResponse.error("Unable to Update Theme")
    #     )

    return SnackResponse.success("Theme Updated")


@router.delete("/themes/{theme_name}")
def delete_theme(theme_name: str, db: Session = Depends(generate_session)):
    """ Deletes theme from the database """
    SiteTheme.delete_theme(db, theme_name)
    # try:
    #     SiteTheme.delete_theme(theme_name)
    # except:
    #     raise HTTPException(
    #         status_code=400, detail=SnackResponse.error("Unable to Delete Theme")
    #     )

    return SnackResponse.success("Theme Deleted")
