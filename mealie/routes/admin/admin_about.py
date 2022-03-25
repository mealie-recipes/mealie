from fastapi import APIRouter

from mealie.core.release_checker import get_latest_version
from mealie.core.settings.static import APP_VERSION
from mealie.routes._base import BaseAdminController, controller
from mealie.schema.admin.about import AdminAboutInfo, AppStatistics, CheckAppConfig

router = APIRouter(prefix="/about")


@controller(router)
class AdminAboutController(BaseAdminController):
    @router.get("", response_model=AdminAboutInfo)
    async def get_app_info(self):
        """Get general application information"""
        settings = self.deps.settings

        return AdminAboutInfo(
            production=settings.PRODUCTION,
            version=APP_VERSION,
            versionLatest=get_latest_version(),
            demo_status=settings.IS_DEMO,
            api_port=settings.API_PORT,
            api_docs=settings.API_DOCS,
            db_type=settings.DB_ENGINE,
            db_url=settings.DB_URL_PUBLIC,
            default_group=settings.DEFAULT_GROUP,
            allow_signup=settings.ALLOW_SIGNUP,
            build_id=settings.GIT_COMMIT_HASH,
        )

    @router.get("/statistics", response_model=AppStatistics)
    async def get_app_statistics(self):

        return AppStatistics(
            total_recipes=self.repos.recipes.count_all(),
            uncategorized_recipes=self.repos.recipes.count_uncategorized(),
            untagged_recipes=self.repos.recipes.count_untagged(),
            total_users=self.repos.users.count_all(),
            total_groups=self.repos.groups.count_all(),
        )

    @router.get("/check", response_model=CheckAppConfig)
    async def check_app_config(self):
        settings = self.deps.settings
        url_set = settings.BASE_URL != "http://localhost:8080"

        return CheckAppConfig(
            email_ready=settings.SMTP_ENABLE,
            ldap_ready=settings.LDAP_ENABLED,
            base_url_set=url_set,
            is_up_to_date=get_latest_version() == APP_VERSION,
        )
