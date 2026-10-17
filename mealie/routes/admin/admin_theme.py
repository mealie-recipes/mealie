from fastapi import APIRouter

from mealie.routes._base import BaseAdminController, controller
from mealie.schema.admin.about import AppTheme

router = APIRouter(prefix="/theme")


@controller(router)
class AdminThemeController(BaseAdminController):
    @router.get("", response_model=AppTheme)
    def get_theme(self):
        """Get the instance-wide theme override, if one has been saved, otherwise the defaults"""
        existing = self.repos.app_theme.get_all(limit=1)
        if existing:
            return existing[0]

        return AppTheme(**self.settings.theme.model_dump())

    @router.put("", response_model=AppTheme)
    def update_theme(self, data: AppTheme):
        """Set the instance-wide theme override, applied to every user regardless of group"""
        existing = self.repos.app_theme.get_all(limit=1)
        if existing:
            return self.repos.app_theme.update(existing[0].id, data)

        return self.repos.app_theme.create(data)

    @router.delete("", status_code=204)
    def reset_theme(self):
        """Remove the instance-wide theme override, reverting to the THEME_* environment defaults"""
        existing = self.repos.app_theme.get_all(limit=1)
        if existing:
            self.repos.app_theme.delete(existing[0].id)
