from app_config import SECRET
from db.database import db
from db.db_setup import create_session
from fastapi_login import LoginManager
from sqlalchemy.orm.session import Session

manager = LoginManager(SECRET, "/api/auth/token")


@manager.user_loader
def query_user(user_email: str, session: Session = None):
    """
    Get a user from the db
    :param user_id: E-Mail of the user
    :return: None or the user object
    """

    session = session if session else create_session()
    user = db.users.get(session, user_email, "email")
    session.close()
    return user
