import enum
from typing import Any, Generic, TypeVar
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from humps import camelize
from pydantic import UUID4, BaseModel, validator
from pydantic.generics import GenericModel

from mealie.schema._mealie import MealieModel

DataT = TypeVar("DataT", bound=BaseModel)


class OrderDirection(str, enum.Enum):
    asc = "asc"
    desc = "desc"


class RecipeSearchQuery(MealieModel):
    cookbook: UUID4 | str | None
    require_all_categories: bool = False
    require_all_tags: bool = False
    require_all_tools: bool = False
    require_all_foods: bool = False
    search: str | None
    _search_seed: str | None = None


class PaginationQuery(MealieModel):
    page: int = 1
    per_page: int = 50
    order_by: str = "created_at"
    order_direction: OrderDirection = OrderDirection.desc
    query_filter: str | None = None
    pagination_seed: str | None = None

    @validator("pagination_seed", always=True, pre=True)
    def validate_randseed(cls, pagination_seed, values):
        if values.get("order_by") == "random" and not pagination_seed:
            raise ValueError("paginationSeed is required when orderBy is random")
        return pagination_seed


class PaginationBase(GenericModel, Generic[DataT]):
    page: int = 1
    per_page: int = 10
    total: int = 0
    total_pages: int = 0
    items: list[DataT]
    next: str | None
    previous: str | None

    def _set_next(self, route: str, query_params: dict[str, Any]) -> None:
        if self.page >= self.total_pages:
            self.next = None
            return

        # combine params with base route
        query_params["page"] = self.page + 1
        self.next = PaginationBase.merge_query_parameters(route, query_params)

    def _set_prev(self, route: str, query_params: dict[str, Any]) -> None:
        if self.page <= 1:
            self.previous = None
            return

        # combine params with base route
        query_params["page"] = self.page - 1
        self.previous = PaginationBase.merge_query_parameters(route, query_params)

    def set_pagination_guides(self, route: str, query_params: dict[str, Any] | None) -> None:
        valid_dict: dict[str, Any] = camelize(query_params) if query_params else {}

        # sanitize user input
        self.page = max(self.page, 1)
        self._set_next(route, valid_dict)
        self._set_prev(route, valid_dict)

    @staticmethod
    def merge_query_parameters(url: str, params: dict[str, Any]):
        scheme, netloc, path, query_string, fragment = urlsplit(url)

        query_params = parse_qs(query_string)
        query_params.update(params)
        new_query_string = urlencode(query_params, doseq=True)

        return urlunsplit((scheme, netloc, path, new_query_string, fragment))
