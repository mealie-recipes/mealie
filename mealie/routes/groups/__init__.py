from datetime import date, timedelta

from fastapi import APIRouter, Depends

from mealie.schema.reports.reports import ReportCategory
from mealie.services._base_http_service import RouterFactory
from mealie.services.group_services import CookbookService, WebhookService
from mealie.services.group_services.meal_service import MealService
from mealie.services.group_services.reports_service import GroupReportService

from . import categories, invitations, migrations, preferences, self_service

router = APIRouter()

router.include_router(self_service.user_router)


webhook_router = RouterFactory(service=WebhookService, prefix="/groups/webhooks", tags=["Groups: Webhooks"])
cookbook_router = RouterFactory(service=CookbookService, prefix="/groups/cookbooks", tags=["Groups: Cookbooks"])


@router.get("/groups/mealplans/today", tags=["Groups: Mealplans"])
def get_todays_meals(m_service: MealService = Depends(MealService.private)):
    return m_service.get_today()


meal_plan_router = RouterFactory(service=MealService, prefix="/groups/mealplans", tags=["Groups: Mealplans"])


@meal_plan_router.get("")
def get_all(start: date = None, limit: date = None, m_service: MealService = Depends(MealService.private)):
    start = start or date.today() - timedelta(days=999)
    limit = limit or date.today() + timedelta(days=999)
    return m_service.get_slice(start, limit)


router.include_router(cookbook_router)
router.include_router(meal_plan_router)
router.include_router(categories.user_router)
router.include_router(webhook_router)
router.include_router(invitations.router, prefix="/groups/invitations", tags=["Groups: Invitations"])
router.include_router(preferences.router, prefix="/groups/preferences", tags=["Group: Preferences"])
router.include_router(migrations.router, prefix="/groups/migrations", tags=["Group: Migrations"])

report_router = RouterFactory(service=GroupReportService, prefix="/groups/reports", tags=["Groups: Reports"])


@report_router.get("")
def get_all_reports(
    report_type: ReportCategory = None, gm_service: GroupReportService = Depends(GroupReportService.private)
):
    return gm_service._get_all(report_type)


router.include_router(report_router)
