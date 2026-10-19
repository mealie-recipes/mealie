# Test cases for authz.yml. Run with `task py:semgrep`.
from fastapi import HTTPException, status

from mealie.routes._base.permissions import forbidden, not_found
from mealie.schema.response import ErrorResponse


def flag_checks(self, user, target_user, permissions):
    # ruleid: mealie-permission-flag-in-handler
    if not self.user.can_invite:
        raise forbidden()

    # ruleid: mealie-permission-flag-in-handler
    if self.user.admin or user.can_manage_household:
        pass

    # ok: mealie-permission-flag-in-handler
    target_user.can_organize = permissions.can_organize


def raw_errors():
    # ruleid: mealie-use-forbidden-not-found
    raise HTTPException(status.HTTP_403_FORBIDDEN)

    # ruleid: mealie-use-forbidden-not-found
    raise HTTPException(status_code=404)

    # ruleid: mealie-use-forbidden-not-found
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail=ErrorResponse.respond(message="Not found."))

    # ruleid: mealie-use-forbidden-not-found
    raise HTTPException(status_code=403, detail=ErrorResponse(message="Permission Denied"))

    # ok: mealie-use-forbidden-not-found
    raise HTTPException(404, "food not found")

    # ok: mealie-use-forbidden-not-found
    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=ErrorResponse.respond("Bad request"))

    # ok: mealie-use-forbidden-not-found
    raise not_found("Not found.")
