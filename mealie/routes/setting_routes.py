from db.db_setup import generate_session
from fastapi import APIRouter, Depends, HTTPException
from services.settings_services import SiteSettings, SiteTheme
from sqlalchemy.orm.session import Session
from utils.post_webhooks import post_webhooks
from utils.snackbar import SnackResponse

router = APIRouter(prefix="/api/site-settings", tags=["Settings"])

@router.get("/")
def get_main_settings(db: Session = Depends(generate_session)):
    """ Returns basic site settings """

    return SiteSettings.get_site_settings(db)


@router.post("/webhooks/test/")
def test_webhooks():
    """ Run the function to test your webhooks """

    return post_webhooks()


@router.post("/update/")
def update_settings(data: SiteSettings, db: Session = Depends(generate_session)):
    """ Returns Site Settings """
    data.update(db)
    # try:
    #     data.update()
    # except:
    #     raise HTTPException(
    #         status_code=400, detail=SnackResponse.error("Unable to Save Settings")
    #     )

    return SnackResponse.success("Settings Updated")


@router.get("/themes/", tags=["Themes"])
def get_all_themes(db: Session = Depends(generate_session)):
    """ Returns all site themes """

    return SiteTheme.get_all(db)


@router.get("/themes/{theme_name}/", tags=["Themes"])
def get_single_theme(theme_name: str, db: Session = Depends(generate_session)):
    """ Returns a named theme """
    return SiteTheme.get_by_name(db, theme_name)


@router.post("/themes/create/", tags=["Themes"])
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


@router.post("/themes/{theme_name}/update/", tags=["Themes"])
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


@router.delete("/themes/{theme_name}/delete/", tags=["Themes"])
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
