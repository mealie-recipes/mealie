from mealie.schema._mealie import MealieModel


class DebugResponse(MealieModel):
    success: bool
    message: str | None = None
