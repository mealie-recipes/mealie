from sqlite3 import IntegrityError

from mealie.lang.providers import AbstractLocaleProvider


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


def mealie_registered_exceptions(t: AbstractLocaleProvider) -> dict:
    """
    This function returns a dictionary of all the globally registered exceptions in the Mealie application.
    """

    return {
        PermissionDenied: t.t("exceptions.permission-denied"),
        NoEntryFound: t.t("exceptions.no-entry-found"),
        IntegrityError: t.t("exceptions.integrity-error"),
    }
