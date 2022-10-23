from sqlite3 import IntegrityError

from mealie.lang.providers import Translator


class UnexpectedNone(Exception):
    """Exception raised when a value is None when it should not be."""

    def __init__(self, message: str = "Unexpected None Value"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


class PermissionDenied(Exception):
    """
    This exception is raised when a user tries to access a resource that they do not have permission to access.
    """

    pass


class NoEntryFound(Exception):
    """
    This exception is raised when a user tries to access a resource that does not exist.
    """

    pass


def mealie_registered_exceptions(t: Translator) -> dict:
    """
    This function returns a dictionary of all the globally registered exceptions in the Mealie application.
    """

    return {
        PermissionDenied: t.t("exceptions.permission-denied"),
        NoEntryFound: t.t("exceptions.no-entry-found"),
        IntegrityError: t.t("exceptions.integrity-error"),
    }
