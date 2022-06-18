import enum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

from mealie.schema._mealie import MealieModel

DataT = TypeVar("DataT", bound=BaseModel)


class OrderDirection(str, enum.Enum):
    asc = "asc"
    desc = "desc"


class PaginationQuery(MealieModel):
    page: int = 1
    per_page: int = 50
    order_by: str = "created_at"
    order_direction: OrderDirection = OrderDirection.desc


class PaginationBase(GenericModel, Generic[DataT]):
    page: int = 1
    per_page: int = 10
    total: int = 0
    total_pages: int = 0
    data: list[DataT]
    next: Optional[str]
    previous: Optional[str]
