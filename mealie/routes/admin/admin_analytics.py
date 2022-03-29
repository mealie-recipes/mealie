from functools import cached_property

from fastapi import APIRouter

from mealie.routes._base import BaseAdminController, controller
from mealie.schema.analytics.analytics import MealieAnalytics
from mealie.services.analytics.service_analytics import AnalyticsService

router = APIRouter(prefix="/analytics")


@controller(router)
class AdminAboutController(BaseAdminController):
    @cached_property
    def service(self) -> AnalyticsService:
        return AnalyticsService(self.repos)

    @router.get("", response_model=MealieAnalytics)
    def get_analytics(self):
        return self.service.calculate_analytics()
