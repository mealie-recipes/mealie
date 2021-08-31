from fastapi import BackgroundTasks, Depends
from sqlalchemy.orm.session import Session

from mealie.schema.user.user import PrivateUser

from .dependencies import generate_session, get_current_user, is_logged_in


class ReadDeps:
    """
    ReadDeps contains the common dependencies for all read operations through the API.
    Note: The user object is used to definer what assets the user has access to.

    Args:
        background_tasks: BackgroundTasks
        session: Session
        user: bool
    """

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        session: Session = Depends(generate_session),
        user=Depends(is_logged_in),
    ):
        self.session: Session = session
        self.bg_task: BackgroundTasks = background_tasks
        self.user: bool = user


class WriteDeps:
    """
    WriteDeps contains the common dependencies for all read operations through the API.
    Note: The user must be logged in or the route will return a 401 error.

    Args:
        background_tasks: BackgroundTasks
        session: Session
        user: UserInDB
    """

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        session: Session = Depends(generate_session),
        user=Depends(get_current_user),
    ):
        self.session: Session = session
        self.bg_task: BackgroundTasks = background_tasks
        self.user: PrivateUser = user
