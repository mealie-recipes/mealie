from fastapi import HTTPException, status

from mealie.schema.user.user import PrivateUser


class OperationChecks:
    """
    OperationChecks class is a mixin class that can be used on routers to provide common permission
    checks and raise the appropriate http error as necessary
    """

    user: PrivateUser

    def __init__(self, user: PrivateUser) -> None:
        self.user = user

    def _raise_unauthorized(self) -> None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    def _raise_forbidden(self) -> None:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    # =========================================
    # User Permission Checks

    def can_manage(self) -> bool:
        if not self.user.can_manage:
            self._raise_forbidden()
        return True

    def can_invite(self) -> bool:
        if not self.user.can_invite:
            self._raise_forbidden()
        return True

    def can_organize(self) -> bool:
        if not self.user.can_organize:
            self._raise_forbidden()
        return True
