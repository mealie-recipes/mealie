from fastapi import HTTPException, status

from mealie.schema.user.user import PrivateUser


class OperationChecks:
    """
    OperationChecks class is a mixin class that can be used on routers to provide common permission
    checks and raise the appropriate http error as necessary
    """

    user: PrivateUser

    ForbiddenException = HTTPException(status.HTTP_403_FORBIDDEN)
    UnauthorizedException = HTTPException(status.HTTP_401_UNAUTHORIZED)

    def __init__(self, user: PrivateUser) -> None:
        self.user = user

    # =========================================
    # User Permission Checks

    def can_manage(self) -> bool:
        if not self.user.can_manage:
            raise self.ForbiddenException
        return True

    def can_invite(self) -> bool:
        if not self.user.can_invite:
            raise self.ForbiddenException
        return True

    def can_organize(self) -> bool:
        if not self.user.can_organize:
            raise self.ForbiddenException
        return True
