from fastapi import APIRouter, Depends

from mealie.schema.reports.reports import ReportCategory
from mealie.services._base_http_service import RouterFactory
from mealie.services.group_services import WebhookService
from mealie.services.group_services.reports_service import GroupReportService

from . import (
    categories,
    controller_cookbooks,
    controller_mealplan,
    invitations,
    labels,
    migrations,
    notifications,
    self_service,
    shopping_lists,
)

router = APIRouter()

router.include_router(self_service.router)


webhook_router = RouterFactory(service=WebhookService, prefix="/groups/webhooks", tags=["Groups: Webhooks"])


router.include_router(controller_mealplan.router)
router.include_router(controller_cookbooks.router)
router.include_router(categories.router)
router.include_router(webhook_router)
router.include_router(invitations.router)
router.include_router(migrations.router)

report_router = RouterFactory(service=GroupReportService, prefix="/groups/reports", tags=["Groups: Reports"])


@report_router.get("")
def get_all_reports(
    report_type: ReportCategory = None,
    gs: GroupReportService = Depends(GroupReportService.private),
):
    return gs._get_all(report_type)


router.include_router(report_router)
router.include_router(shopping_lists.router)
router.include_router(labels.router)
router.include_router(notifications.router)
