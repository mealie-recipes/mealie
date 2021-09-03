from abc import abstractmethod
from typing import TypeVar

from mealie.core.dependencies.grouped import AdminDeps, PublicDeps, UserDeps

from .base_http_service import BaseHttpService

T = TypeVar("T")
D = TypeVar("D")


class PublicHttpService(BaseHttpService[T, D]):
    """
    PublicHttpService sets the class methods to PublicDeps for read actions
    and UserDeps for write actions which are inaccessible to not logged in users.
    """

    read_existing = BaseHttpService._existing_factory(PublicDeps)
    write_existing = BaseHttpService._existing_factory(UserDeps)

    public = BaseHttpService._class_method_factory(PublicDeps)
    private = BaseHttpService._class_method_factory(UserDeps)

    @abstractmethod
    def populate_item(self) -> None:
        ...


class UserHttpService(BaseHttpService[T, D]):
    """
    UserHttpService sets the class methods to UserDeps which are inaccessible
    to not logged in users.
    """

    read_existing = BaseHttpService._existing_factory(UserDeps)
    write_existing = BaseHttpService._existing_factory(UserDeps)

    public = BaseHttpService._class_method_factory(UserDeps)
    private = BaseHttpService._class_method_factory(UserDeps)

    @abstractmethod
    def populate_item(self) -> None:
        ...


class AdminHttpService(BaseHttpService[T, D]):
    """
    AdminHttpService restricts the class methods to AdminDeps which are restricts
    all class methods to users who are administrators.
    """

    read_existing = BaseHttpService._existing_factory(AdminDeps)
    write_existing = BaseHttpService._existing_factory(AdminDeps)

    public = BaseHttpService._class_method_factory(AdminDeps)
    private = BaseHttpService._class_method_factory(AdminDeps)

    @abstractmethod
    def populate_item(self) -> None:
        ...
