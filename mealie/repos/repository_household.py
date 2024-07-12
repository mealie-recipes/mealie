from mealie.db.models.household.household import Household
from mealie.repos.repository_generic import GroupRepositoryGeneric
from mealie.schema.household.household import HouseholdOut


class RepositoryHousehold(GroupRepositoryGeneric[HouseholdOut, Household]): ...
