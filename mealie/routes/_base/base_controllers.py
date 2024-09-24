from abc import ABC
from logging import Logger

from fastapi import Depends, HTTPException
from pydantic import UUID4, ConfigDict
from sqlalchemy.orm import Session

from mealie.core.config import get_app_dirs, get_app_settings
from mealie.core.dependencies.dependencies import (
    get_admin_user,
    get_current_user,
    get_integration_id,
    get_public_group,
)
from mealie.core.exceptions import mealie_registered_exceptions
from mealie.core.root_logger import get_logger
from mealie.core.settings.directories import AppDirectories
from mealie.core.settings.settings import AppSettings
from mealie.db.db_setup import generate_session
from mealie.lang import local_provider
from mealie.lang.providers import Translator
from mealie.repos._utils import NOT_SET, NotSet
from mealie.repos.all_repositories import AllRepositories, get_repositories
from mealie.routes._base.checks import OperationChecks
from mealie.schema.household.household import HouseholdInDB
from mealie.schema.user.user import GroupInDB, PrivateUser
from mealie.services.event_bus_service.event_bus_service import EventBusService
from mealie.services.event_bus_service.event_types import EventDocumentDataBase, EventTypes


class _BaseController(ABC):  # noqa: B024
    session: Session = Depends(generate_session)
    translator: Translator = Depends(local_provider)

    _repos: AllRepositories | None = None
    _logger: Logger | None = None
    _settings: AppSettings | None = None
    _folders: AppDirectories | None = None

    @property
    def t(self):
        return self.translator.t if self.translator else local_provider().t

    @property
    def repos(self):
        if not self._repos:
            self._repos = AllRepositories(self.session, group_id=self.group_id, household_id=self.household_id)
        return self._repos

    @property
    def logger(self) -> Logger:
        if not self._logger:
            self._logger = get_logger()
        return self._logger

    @property
    def settings(self) -> AppSettings:
        if not self._settings:
            self._settings = get_app_settings()
        return self._settings

    @property
    def folders(self) -> AppDirectories:
        if not self._folders:
            self._folders = get_app_dirs()
        return self._folders

    @property
    def group_id(self) -> UUID4 | None | NotSet:
        return NOT_SET

    @property
    def household_id(self) -> UUID4 | None | NotSet:
        return NOT_SET

    model_config = ConfigDict(arbitrary_types_allowed=True)


class BasePublicController(_BaseController):
    """
    This is a public class for all User restricted controllers in the API.
    It includes the common SharedDependencies and some common methods used
    by all Admin controllers.
    """

    ...


class BasePublicGroupExploreController(BasePublicController):
    """
    Base class for all controllers that are public and explore group data.
    """

    group: GroupInDB = Depends(get_public_group)

    @property
    def group_id(self) -> UUID4 | None | NotSet:
        return self.group.id

    def get_public_household(self, household_slug_or_id: str | UUID4) -> HouseholdInDB:
        household = self.repos.households.get_by_slug_or_id(household_slug_or_id)
        if not household or household.preferences.private_household:
            raise HTTPException(404, "household not found")
        return household

    def get_explore_url_path(self, endpoint: str) -> str:
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return f"/explore/groups/{self.group.slug}/{endpoint}"


class BasePublicHouseholdExploreController(BasePublicGroupExploreController):
    """
    Base class for all controllers that are public and explore household data.
    """

    @property
    def cross_household_repos(self):
        """
        Household-level repos with no household filter. Public controllers don't have access to a household identifier;
        instead, they return all public data, filtered by the household preferences.

        When using this repo, the caller should filter by household preferences, e.g.:

        `household.preferences.privateHousehold = FALSE`
        """
        return get_repositories(self.session, group_id=self.group_id, household_id=None)


class BaseUserController(_BaseController):
    """
    This is a base class for all User restricted controllers in the API.
    It includes the common SharedDependencies and some common methods used
    by all Admin controllers.
    """

    user: PrivateUser = Depends(get_current_user)
    integration_id: str = Depends(get_integration_id)
    translator: Translator = Depends(local_provider)

    # Manual Cache
    _checks: OperationChecks

    def registered_exceptions(self, ex: type[Exception]) -> str:
        registered = {
            **mealie_registered_exceptions(self.translator),
        }
        return registered.get(ex, self.t("generic.server-error"))

    @property
    def group_id(self) -> UUID4:
        return self.user.group_id

    @property
    def household_id(self) -> UUID4:
        return self.user.household_id

    @property
    def group(self) -> GroupInDB:
        return self.repos.groups.get_one(self.group_id)

    @property
    def household(self) -> HouseholdInDB:
        return self.repos.households.get_one(self.household_id)

    @property
    def checks(self) -> OperationChecks:
        if not self._checks:
            self._checks = OperationChecks(self.user)
        return self._checks


class BaseAdminController(BaseUserController):
    """
    This is a base class for all Admin restricted controllers in the API.
    It includes the common Shared Dependencies and some common methods used
    by all Admin controllers.
    """

    user: PrivateUser = Depends(get_admin_user)

    @property
    def repos(self):
        if not self._repos:
            # Admins have access to all groups and households, so we don't want to filter by group_id or household_id
            self._repos = AllRepositories(self.session, group_id=None, household_id=None)
        return self._repos


class BaseCrudController(BaseUserController):
    """
    Base class for all CRUD controllers to facilitate common CRUD functions.
    """

    event_bus: EventBusService = Depends(EventBusService.as_dependency)

    def publish_event(
        self,
        event_type: EventTypes,
        document_data: EventDocumentDataBase,
        group_id: UUID4,
        household_id: UUID4 | None,
        message: str = "",
    ) -> None:
        self.event_bus.dispatch(
            integration_id=self.integration_id,
            group_id=group_id,
            household_id=household_id,
            event_type=event_type,
            document_data=document_data,
            message=message,
        )
