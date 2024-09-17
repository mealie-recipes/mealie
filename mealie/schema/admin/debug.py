from mealie.schema._mealie import MealieModel


class DebugResponse(MealieModel):
    success: bool
    response: str | None = None
