from mealie.core import exceptions
from mealie.lang import local_provider


def test_mealie_registered_exceptions() -> None:
    provider = local_provider()

    lookup = exceptions.mealie_registered_exceptions(provider)

    assert "permission" in lookup[exceptions.PermissionDenied]
    assert "The requested resource was not found" in lookup[exceptions.NoEntryFound]
    assert "integrity" in lookup[exceptions.IntegrityError]
