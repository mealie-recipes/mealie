from abc import ABC
from logging import Logger

from fastapi import Depends
from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.core.config import get_app_dirs, get_app_settings
from mealie.core.dependencies.dependencies import get_admin_user, get_current_user
from mealie.core.exceptions import mealie_registered_exceptions
from mealie.core.root_logger import get_logger
from mealie.core.settings.directories import AppDirectories
from mealie.core.settings.settings import AppSettings
from mealie.db.db_setup import generate_session
from mealie.lang import local_provider
from mealie.lang.providers import Translator
from mealie.repos.all_repositories import AllRepositories
from mealie.routes._base.checks import OperationChecks
from mealie.schema.user.user import GroupInDB, PrivateUser


class _BaseController(ABC):
    session: Session = Depends(generate_session)
    translator: Translator = Depends(local_provider)

    _repos: AllRepositories | None
    _logger: Logger | None
    _settings: AppSettings | None
    _folders: AppDirectories | None

    @property
    def t(self):
        return self.translator.t if self.translator else local_provider().t

    @property
    def repos(self):
        if not self._repos:
            self._repos = AllRepositories(self.session)
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

    class Config:
        arbitrary_types_allowed = True


class BasePublicController(_BaseController):
    """
    This is a public class for all User restricted controllers in the API.
    It includes the common SharedDependencies and some common methods used
    by all Admin controllers.
    """

    ...


class BaseUserController(_BaseController):
    """
    This is a base class for all User restricted controllers in the API.
    It includes the common SharedDependencies and some common methods used
    by all Admin controllers.
    """

    user: PrivateUser = Depends(get_current_user)
    translator: Translator = Depends(local_provider)

    # Manual Cache
    _checks: OperationChecks

    def registered_exceptions(self, ex: type[Exception]) -> str:
        registered = {
            **mealie_registered_exceptions(self.translator),
        }
        return registered.get(ex, "An unexpected error occurred.")

    @property
    def group_id(self) -> UUID4:
        return self.user.group_id

    @property
    def group(self) -> GroupInDB:
        return self.repos.groups.get_one(self.group_id)

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
