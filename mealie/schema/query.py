from mealie.schema._mealie import MealieModel


class GetAll(MealieModel):
    start: int = 0
    limit: int = 999
    order_by: str = "date_added"
    order_descending: bool = True
