from mealie.schema._mealie import MealieModel


class GetAll(MealieModel):
    start: int = 0
    limit: int = 999
