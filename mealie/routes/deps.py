from mealie.core.config import SECRET
from mealie.db.database import db
from mealie.db.db_setup import create_session
from fastapi_login import LoginManager
from sqlalchemy.orm.session import Session

from mealie.schema.user import UserInDB

manager = LoginManager(SECRET, "/api/auth/token")


@manager.user_loader
def query_user(user_email: str, session: Session = None) -> UserInDB:
    """
    Get a user from the db
    :param user_id: E-Mail of the user
    :return: None or the UserInDB object
    """

    session = session if session else create_session()
    user = db.users.get(session, user_email, "email")
    session.close()
    return user
