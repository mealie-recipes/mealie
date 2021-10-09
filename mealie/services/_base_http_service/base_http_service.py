from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Type, TypeVar

from fastapi import BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_dirs, get_app_settings
from mealie.core.root_logger import get_logger
from mealie.db.database import get_database
from mealie.db.db_setup import SessionLocal
from mealie.lang import get_locale_provider
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
        self.db = get_database(session)
        self.app_dirs = get_app_dirs()
        self.settings = get_app_settings()
        self.t = get_locale_provider().t

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

    @classmethod
    @abstractmethod
    def public(cls, deps: Any):
        pass

    @classmethod
    @abstractmethod
    def private(cls, deps: Any):
        pass

    @classmethod
    @abstractmethod
    def read_existing(cls, deps: Any):
        pass

    @classmethod
    @abstractmethod
    def write_existing(cls, deps: Any):
        pass

    @abstractmethod
    def populate_item(self) -> None:
        pass

    @property
    def group_id(self):
        # TODO: Populate Group in Private User Call WARNING: May require significant refactoring
        if not self._group_id_cache:
            group = self.db.groups.get(self.user.group, "name")
            self._group_id_cache = group.id
        return self._group_id_cache

    def cast(self, item: BaseModel, dest, assign_owner=True) -> T:
        """cast a pydantic model to the destination type

        Args:
            item (BaseModel): A pydantic model containing data
            dest ([type]): A type to cast the data to
            assign_owner (bool, optional): If true, will assign the user_id and group_id to the dest type. Defaults to True.

        Returns:
            TypeVar(dest): Returns the destionation model type
        """
        data = item.dict()

        if assign_owner:
            data["user_id"] = self.user.id
            data["group_id"] = self.group_id

        return dest(**data)

    def assert_existing(self, id: T) -> None:
        self.populate_item(id)
        self._check_item()

    def _check_item(self) -> None:
        if not self.item:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if self.__class__._restrict_by_group:
            group_id = getattr(self.item, "group_id", False)

            if not group_id or group_id != self.group_id:
                raise HTTPException(status.HTTP_403_FORBIDDEN)

        if hasattr(self, "check_item"):
            self.check_item()

    def _create_event(self, title: str, message: str) -> None:
        if not self.__class__.event_func:
            raise NotImplementedError("`event_func` must be set by child class")

        self.background_tasks.add_task(self.__class__.event_func, title, message, self.session)
