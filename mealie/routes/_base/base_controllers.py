from abc import ABC
from functools import cached_property

from fastapi import Depends
from pydantic import UUID4

from mealie.core.exceptions import mealie_registered_exceptions
from mealie.repos.all_repositories import AllRepositories
from mealie.routes._base.checks import OperationChecks
from mealie.routes._base.dependencies import SharedDependencies
from mealie.schema.user.user import GroupInDB, PrivateUser


class BasePublicController(ABC):
    """
    This is a public class for all User restricted controllers in the API.
    It includes the common SharedDependencies and some common methods used
    by all Admin controllers.
    """

    deps: SharedDependencies = Depends(SharedDependencies.public)


class BaseUserController(ABC):
    """
    This is a base class for all User restricted controllers in the API.
    It includes the common SharedDependencies and some common methods used
    by all Admin controllers.
    """

    deps: SharedDependencies = Depends(SharedDependencies.user)

    def registered_exceptions(self, ex: type[Exception]) -> str:
        registered = {
            **mealie_registered_exceptions(self.deps.t),
        }
        return registered.get(ex, "An unexpected error occurred.")

    @cached_property
    def repos(self):
        return AllRepositories(self.deps.session)

    @property
    def group_id(self) -> UUID4:
        return self.deps.acting_user.group_id

    @property
    def user(self) -> PrivateUser:
        return self.deps.acting_user

    @property
    def group(self) -> GroupInDB:
        return self.deps.repos.groups.get_one(self.group_id)

    @cached_property
    def checks(self) -> OperationChecks:
        return OperationChecks(self.deps.acting_user)


class BaseAdminController(BaseUserController):
    """
    This is a base class for all Admin restricted controllers in the API.
    It includes the common Shared Dependencies and some common methods used
    by all Admin controllers.
    """

    deps: SharedDependencies = Depends(SharedDependencies.admin)
