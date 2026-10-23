from pydantic import UUID4, ConfigDict

from mealie.schema._mealie import MealieModel


class ReadMealPlanICalToken(MealieModel):
    household_id: UUID4
    mealplan_ical_token: str | None = None
    model_config = ConfigDict(from_attributes=True)
