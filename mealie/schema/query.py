from typing import Optional

from mealie.schema._mealie import MealieModel


class GetAll(MealieModel):
    start: int = 0
    limit: int = 999
    order_by: Optional[str]
    order_descending: Optional[bool] = True
