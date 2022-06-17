from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationQuery


class GetAll(MealieModel, PaginationQuery):
    ...
