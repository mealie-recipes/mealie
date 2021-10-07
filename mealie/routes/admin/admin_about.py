from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_settings
from mealie.core.settings.static import APP_VERSION
from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.schema.admin.about import AdminAboutInfo, AppStatistics, CheckAppConfig

router = APIRouter(prefix="/about")


@router.get("", response_model=AdminAboutInfo)
async def get_app_info():
    """ Get general application information """
    settings = get_app_settings()

    return AdminAboutInfo(
        production=settings.PRODUCTION,
        version=APP_VERSION,
        demo_status=settings.IS_DEMO,
        api_port=settings.API_PORT,
        api_docs=settings.API_DOCS,
        db_type=settings.DB_ENGINE,
        db_url=settings.DB_URL_PUBLIC,
        default_group=settings.DEFAULT_GROUP,
    )


@router.get("/statistics", response_model=AppStatistics)
async def get_app_statistics(session: Session = Depends(generate_session)):
    db = get_database(session)
    return AppStatistics(
        total_recipes=db.recipes.count_all(),
        uncategorized_recipes=db.recipes.count_uncategorized(),
        untagged_recipes=db.recipes.count_untagged(),
        total_users=db.users.count_all(),
        total_groups=db.groups.count_all(),
    )


@router.get("/check", response_model=CheckAppConfig)
async def check_app_config():
    settings = get_app_settings()

    url_set = settings.BASE_URL != "http://localhost:8080"

    return CheckAppConfig(
        email_ready=settings.SMTP_ENABLE,
        base_url_set=url_set,
    )
