from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_dirs, get_settings
from mealie.core.dependencies import WriteDeps
from mealie.core.root_logger import get_logger
from mealie.core.security import hash_password, verify_password
from mealie.db.database import get_database
from mealie.db.db_setup import SessionLocal
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.user.user import ChangePassword, PrivateUser
from mealie.services.events import create_user_event

logger = get_logger(module=__name__)


class UserService:
    def __init__(self, session: Session, acting_user: PrivateUser, background_tasks: BackgroundTasks = None) -> None:
        self.session = session or SessionLocal()
        self.acting_user = acting_user
        self.background_tasks = background_tasks
        self.recipe: Recipe = None

        # Global Singleton Dependency Injection
        self.db = get_database()
        self.app_dirs = get_app_dirs()
        self.settings = get_settings()

    @classmethod
    def write_existing(cls, id: int, deps: WriteDeps = Depends()):
        new_instance = cls(session=deps.session, acting_user=deps.user, background_tasks=deps.bg_task)
        new_instance._populate_target_user(id)
        new_instance._assert_user_change_allowed()
        return new_instance

    def _assert_user_change_allowed(self) -> None:
        if self.acting_user.id != self.target_user.id and not self.acting_user.admin:
            # only admins can edit other users
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="NOT_AN_ADMIN")

    def _populate_target_user(self, id: int = None):
        if id:
            self.target_user = self.db.users.get(self.session, id)
            if not self.target_user:
                raise HTTPException(status.HTTP_404_NOT_FOUND)
        else:
            self.target_user = self.acting_user

    def _create_event(self, title: str, message: str) -> None:
        self.background_tasks.add_task(create_user_event, title, message, self.session)

    def change_password(self, password_change: ChangePassword) -> PrivateUser:
        """"""
        if not verify_password(password_change.current_password, self.target_user.password):
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

        self.target_user.password = hash_password(password_change.new_password)

        return self.db.users.update_password(self.session, self.target_user.id, self.target_user.password)
