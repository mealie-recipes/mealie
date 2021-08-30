from typing import Callable, Generic, TypeVar

from fastapi import BackgroundTasks, Depends
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_dirs, get_settings
from mealie.core.dependencies.grouped import ReadDeps, WriteDeps
from mealie.core.root_logger import get_logger
from mealie.db.database import get_database
from mealie.db.db_setup import SessionLocal
from mealie.schema.user.user import PrivateUser

logger = get_logger()

T = TypeVar("T")
D = TypeVar("D")


class BaseHttpService(Generic[T, D]):
    """The BaseHttpService class is a generic class that can be used to create
    http services that are injected via `Depends` into a route function. To use,
    you must define the Generic type arguments:

    `T`: The type passed into the *_existing functions (e.g. id) which is then passed into assert_existing
    `D`: Not yet implemented

    Child Requirements:
        Define the following functions:
            `assert_existing(self, data: T) -> None:`

        Define the following variables:
            `event_func`: A function that is called when an event is created.
    """

    event_func: Callable = None

    def __init__(self, session: Session, user: PrivateUser, background_tasks: BackgroundTasks = None) -> None:
        self.session = session or SessionLocal()
        self.user = user
        self.logged_in = bool(self.user)
        self.background_tasks = background_tasks

        # Static Globals Dependency Injection
        self.db = get_database()
        self.app_dirs = get_app_dirs()
        self.settings = get_settings()

    def assert_existing(self, data: T) -> None:
        raise NotImplementedError("`assert_existing` must by implemented by child class")

    @classmethod
    def read_existing(cls, id: T, deps: ReadDeps = Depends()):
        """
        Used for dependency injection for routes that require an existing recipe. If the recipe doesn't exist
        or the user doens't not have the required permissions, the proper HTTP Status code will be raised.

        Args:
            slug (str): Recipe Slug used to query the database
            session (Session, optional): The Injected SQLAlchemy Session.
            user (bool, optional): The injected determination of is_logged_in.

        Raises:
            HTTPException: 404 Not Found
            HTTPException: 403 Forbidden

        Returns:
            RecipeService: The Recipe Service class with a populated recipe attribute
        """
        new_class = cls(deps.session, deps.user, deps.bg_tasks)
        new_class.assert_existing(id)
        return new_class

    @classmethod
    def write_existing(cls, id: T, deps: WriteDeps = Depends()):
        """
        Used for dependency injection for routes that require an existing recipe. The only difference between
        read_existing and write_existing is that the user is required to be logged in on write_existing method.

        Args:
            slug (str): Recipe Slug used to query the database
            session (Session, optional): The Injected SQLAlchemy Session.
            user (bool, optional): The injected determination of is_logged_in.

        Raises:
            HTTPException: 404 Not Found
            HTTPException: 403 Forbidden

        Returns:
            RecipeService: The Recipe Service class with a populated recipe attribute
        """
        new_class = cls(deps.session, deps.user, deps.bg_task)
        new_class.assert_existing(id)
        return new_class

    @classmethod
    def base(cls, deps: WriteDeps = Depends()):
        """A Base instance to be used as a router dependency

        Raises:
            HTTPException: 400 Bad Request

        """
        return cls(deps.session, deps.user, deps.bg_task)

    def _create_event(self, title: str, message: str) -> None:
        if not self.__class__.event_func:
            raise NotImplementedError("`event_func` must be set by child class")

        self.background_tasks.add_task(self.__class__.event_func, title, message, self.session)
