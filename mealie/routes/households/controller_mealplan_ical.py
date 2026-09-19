from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from mealie.db.db_setup import generate_session
from mealie.lang import get_locale_provider
from mealie.lang.providers import Translator
from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.schema.meal_plan.mealplan_ical import ReadMealPlanICalToken
from mealie.schema.response.responses import ErrorResponse
from mealie.services.household_services.mealplan_ical_service import (
    MealPlanICalQuery,
    MealPlanICalService,
    generate_ical_token,
)

router = APIRouter(prefix="/households/mealplans/ical", tags=["Households: Meal Plans"])
# the feed is public, so it can't share the controller's router
public_router = APIRouter(prefix="/households/mealplans/ical", tags=["Households: Meal Plans"])


@controller(router)
class MealplanICalController(BaseUserController):
    def _get_token(self) -> ReadMealPlanICalToken:
        prefs = self.repos.household_preferences.get_one(
            self.household_id, key="household_id", override_schema=ReadMealPlanICalToken
        )
        if not prefs:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=ErrorResponse.respond("Household not found"))
        return prefs

    def _set_token(self, token: str | None) -> ReadMealPlanICalToken:
        self.checks.can_manage_household()
        self.repos.household_preferences.update(self.household_id, {"mealplan_ical_token": token})
        return self._get_token()

    @router.get("", response_model=ReadMealPlanICalToken)
    def get_ical_token(self):
        """Returns the token for the household's meal plan iCal feed, or null if the feed is disabled"""
        return self._get_token()

    @router.post("", response_model=ReadMealPlanICalToken)
    def create_ical_token(self):
        """Enables the meal plan iCal feed, replacing any existing token so old feed URLs stop working"""
        return self._set_token(generate_ical_token())

    @router.delete("", response_model=ReadMealPlanICalToken)
    def delete_ical_token(self):
        """Disables the meal plan iCal feed"""
        return self._set_token(None)


@public_router.get("/{token}", response_class=Response)
def get_mealplan_ical_feed(
    token: str,
    query: Annotated[MealPlanICalQuery, Query()],
    session: Session = Depends(generate_session),
    translator: Translator = Depends(get_locale_provider),
) -> Response:
    """
    Public iCal feed of the household's meal plan. No authentication is required;
    access is controlled by the secret token in the URL.
    """
    feed = MealPlanICalService(session, translator).get_feed(token, query)
    if feed is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=ErrorResponse.respond("Calendar not found"))

    return Response(
        content=feed,
        media_type="text/calendar",
        headers={"Content-Disposition": 'inline; filename="mealplan.ics"', "Cache-Control": "no-cache"},
    )
