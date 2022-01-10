from abc import ABC
from functools import cached_property

from fastapi import Depends

from mealie.repos.all_repositories import AllRepositories
from mealie.routes._base.dependencies import SharedDependencies


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


class BaseAdminController(ABC):
    """
    This is a base class for all Admin restricted controllers in the API.
    It includes the common Shared Dependencies and some common methods used
    by all Admin controllers.
    """

    deps: SharedDependencies = Depends(SharedDependencies.admin)

    @cached_property
    def repos(self):
        return AllRepositories(self.deps.session)
