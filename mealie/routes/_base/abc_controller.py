from abc import ABC
from functools import cached_property

from fastapi import Depends

from mealie.repos.all_repositories import AllRepositories
from mealie.routes._base.checks import OperationChecks
from mealie.routes._base.dependencies import SharedDependencies


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

    @cached_property
    def repos(self):
        return AllRepositories(self.deps.session)

    @property
    def group_id(self):
        return self.deps.acting_user.group_id

    @property
    def user(self):
        return self.deps.acting_user

    @property
    def group(self):
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
