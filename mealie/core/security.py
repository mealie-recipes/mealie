from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a plain string to a hashed password

    Args:
        plain_password (str): raw password string
        hashed_password (str): hashed password from the database

    Returns:
        bool: Returns True if a match return False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Takes in a raw password and hashes it. Used prior to saving
    a new password to the database.

    Args:
        password (str): Password String

    Returns:
        str: Hashed Password
    """
    return pwd_context.hash(password)
