from abc import ABC, abstractmethod
from typing import Callable, Generic, Type, TypeVar

from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_dirs, get_settings
from mealie.core.dependencies.grouped import PublicDeps, UserDeps
from mealie.core.root_logger import get_logger
from mealie.db.database import get_database
from mealie.db.db_setup import SessionLocal
from mealie.schema.user.user import PrivateUser

logger = get_logger()

T = TypeVar("T")
D = TypeVar("D")


CLS_DEP = TypeVar("CLS_DEP")  # Generic Used for the class method dependencies


class BaseHttpService(Generic[T, D], ABC):
    """
    The BaseHttpService class is a generic class that can be used to create
    http services that are injected via `Depends` into a route function. To use,
    you must define the Generic type arguments:

    `T`: The type passed into the *_existing functions (e.g. id) which is then passed into assert_existing
    `D`: Item returned from database layer
    """

    item: D = None

    # Function that Generate Corrsesponding Routes through RouterFactory:
    # if the method is defined or != `None` than the corresponding route is defined through the RouterFactory.
    # If the method is not defined, then the route will be excluded from creation. This service based articheture
    # is being adopted as apart of the v1 migration
    get_all: Callable = None
    create_one: Callable = None
    update_one: Callable = None
    update_many: Callable = None
    populate_item: Callable = None
    delete_one: Callable = None
    delete_all: Callable = None

    # Type Definitions
    _schema = None
    _create_schema = None
    _update_schema = None

    # Function called to create a server side event
    event_func: Callable = None

    # Config
    _restrict_by_group = False
    _group_id_cache = None

    def __init__(self, session: Session, user: PrivateUser, background_tasks: BackgroundTasks = None) -> None:
        self.session = session or SessionLocal()
        self.user = user
        self.logged_in = bool(self.user)
        self.background_tasks = background_tasks

        # Static Globals Dependency Injection
        self.db = get_database()
        self.app_dirs = get_app_dirs()
        self.settings = get_settings()

    @property
    def group_id(self):
        # TODO: Populate Group in Private User Call WARNING: May require significant refactoring
        if not self._group_id_cache:
            group = self.db.groups.get(self.session, self.user.group, "name")
            self._group_id_cache = group.id
        return self._group_id_cache

    def _existing_factory(dependency: Type[CLS_DEP]) -> classmethod:
        def cls_method(cls, item_id: T, deps: CLS_DEP = Depends(dependency)):
            new_class = cls(deps.session, deps.user, deps.bg_task)
            new_class.assert_existing(item_id)
            return new_class

        return classmethod(cls_method)

    def _class_method_factory(dependency: Type[CLS_DEP]) -> classmethod:
        def cls_method(cls, deps: CLS_DEP = Depends(dependency)):
            return cls(deps.session, deps.user, deps.bg_task)

        return classmethod(cls_method)

    # TODO: Refactor to allow for configurable dependencies base on substantiation
    read_existing = _existing_factory(PublicDeps)
    write_existing = _existing_factory(UserDeps)

    public = _class_method_factory(PublicDeps)
    private = _class_method_factory(UserDeps)

    def assert_existing(self, id: T) -> None:
        self.populate_item(id)
        self._check_item()

    @abstractmethod
    def populate_item(self) -> None:
        ...

    def _check_item(self) -> None:
        if not self.item:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if self.__class__._restrict_by_group:
            group_id = getattr(self.item, "group_id", False)

            if not group_id or group_id != self.group_id:
                raise HTTPException(status.HTTP_403_FORBIDDEN)

    def _create_event(self, title: str, message: str) -> None:
        if not self.__class__.event_func:
            raise NotImplementedError("`event_func` must be set by child class")

        self.background_tasks.add_task(self.__class__.event_func, title, message, self.session)
