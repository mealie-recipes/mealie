import enum
from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

DataT = TypeVar("DataT", bound=BaseModel)


class OrderDirection(str, enum.Enum):
    asc = "asc"
    desc = "desc"


class PaginationQuery(BaseModel):
    page: int = 1
    order_by: str = "created_at"
    order_direction: OrderDirection = OrderDirection.desc
    per_page: int = 50


class PaginationBase(GenericModel, Generic[DataT]):
    page: int = 1
    per_page: int = 10
    total: int = 0
    total_pages: int = 0
    data: list[DataT]
