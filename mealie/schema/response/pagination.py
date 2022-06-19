import enum
from typing import Any, Generic, Optional, TypeVar
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from humps import camelize
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

    def _set_next(self, route: str, query_params: dict[str, Any]) -> None:
        if self.page >= self.total_pages:
            self.next = None
            return

        # combine params with base route
        query_params.update({"page": self.page + 1})
        self.next = PaginationBase.merge_query_parameters(route, query_params)

    def _set_prev(self, route: str, query_params: dict[str, Any]) -> None:
        if self.page <= 1:
            self.previous = None
            return

        # combine params with base route
        query_params.update({"page": self.page - 1})
        self.previous = PaginationBase.merge_query_parameters(route, query_params)

    def set_pagination_guides(self, route: str, query_params: Optional[dict[str, Any]]) -> None:
        if not query_params:
            query_params = {}

        query_params = camelize(query_params)

        # sanitize user input
        if self.page < 1:
            self.page = 1

        self._set_next(route, query_params)
        self._set_prev(route, query_params)

    @staticmethod
    def merge_query_parameters(url: str, params: dict[str, Any]):
        scheme, netloc, path, query_string, fragment = urlsplit(url)

        query_params = parse_qs(query_string)
        query_params.update(params)
        new_query_string = urlencode(query_params, doseq=True)

        return urlunsplit((scheme, netloc, path, new_query_string, fragment))
