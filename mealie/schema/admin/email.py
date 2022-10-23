from mealie.schema._mealie import MealieModel


class EmailReady(MealieModel):
    ready: bool


class EmailSuccess(MealieModel):
    success: bool
    error: str | None = None


class EmailTest(MealieModel):
    email: str
