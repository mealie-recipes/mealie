from pydantic import UUID4

from .._mealie import MealieModel


class MealieAnalytics(MealieModel):
    installation_id: UUID4
    version: str
    database_type: str

    using_email: bool
    using_ldap: bool

    api_tokens: int
    users: int
    groups: int
    recipes: int
    shopping_lists: int
    cookbooks: int
