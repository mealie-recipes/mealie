from __future__ import annotations

from functools import cached_property
from logging import Logger

from fastapi import Depends
from sqlalchemy.orm import Session

from mealie.core.config import get_app_dirs, get_app_settings
from mealie.core.dependencies.dependencies import get_admin_user, get_current_user
from mealie.core.root_logger import get_logger
from mealie.core.settings.directories import AppDirectories
from mealie.core.settings.settings import AppSettings
from mealie.db.db_setup import generate_session
from mealie.lang import AbstractLocaleProvider, get_locale_provider
from mealie.repos import AllRepositories
from mealie.schema.user.user import PrivateUser


class SharedDependencies:
    session: Session
    t: AbstractLocaleProvider
    acting_user: PrivateUser | None

    def __init__(self, session: Session, acting_user: PrivateUser | None) -> None:
        self.t = get_locale_provider()
        self.session = session
        self.acting_user = acting_user

    @classmethod
    def public(cls, session: Session = Depends(generate_session)) -> "SharedDependencies":
        return cls(session, None)

    @classmethod
    def user(
        cls,
        session: Session = Depends(generate_session),
        user: PrivateUser = Depends(get_current_user),
    ) -> "SharedDependencies":
        return cls(session, user)

    @classmethod
    def admin(
        cls,
        session: Session = Depends(generate_session),
        admin: PrivateUser = Depends(get_admin_user),
    ) -> "SharedDependencies":
        return cls(session, admin)

    @cached_property
    def logger(self) -> Logger:
        return get_logger()

    @cached_property
    def settings(self) -> AppSettings:
        return get_app_settings()

    @cached_property
    def folders(self) -> AppDirectories:
        return get_app_dirs()

    @cached_property
    def repos(self) -> AllRepositories:
        return AllRepositories(self.session)
