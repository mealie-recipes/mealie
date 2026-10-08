from mealie.core import exceptions
from mealie.lang import get_locale_provider


def test_mealie_registered_exceptions() -> None:
    provider = get_locale_provider()

    lookup = exceptions.mealie_registered_exceptions(provider)

    assert lookup[exceptions.PermissionDenied] == "You do not have permission to perform this action"
    assert "The requested resource was not found" in lookup[exceptions.NoEntryFound]
    assert "integrity" in lookup[exceptions.IntegrityError]
