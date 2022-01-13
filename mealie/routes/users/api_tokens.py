from datetime import timedelta

from fastapi import HTTPException, status

from mealie.core.security import create_access_token
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.user import CreateToken, LoingLiveTokenIn, LongLiveTokenInDB

router = UserAPIRouter(prefix="/users", tags=["Users: Tokens"])


@controller(router)
class UserApiTokensController(BaseUserController):
    @router.post("/api-tokens", status_code=status.HTTP_201_CREATED)
    def create_api_token(
        self,
        token_name: LoingLiveTokenIn,
    ):
        """Create api_token in the Database"""

        token_data = {"long_token": True, "id": str(self.user.id)}

        five_years = timedelta(1825)
        token = create_access_token(token_data, five_years)

        token_model = CreateToken(
            name=token_name.name,
            token=token,
            user_id=self.user.id,
        )

        new_token_in_db = self.repos.api_tokens.create(token_model)

        if new_token_in_db:
            return {"token": token}

    @router.delete("/api-tokens/{token_id}")
    def delete_api_token(self, token_id: int):
        """Delete api_token from the Database"""
        token: LongLiveTokenInDB = self.repos.api_tokens.get(token_id)

        if not token:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Could not locate token with id '{token_id}' in database")

        if token.user.email == self.user.email:
            deleted_token = self.repos.api_tokens.delete(token_id)
            return {"token_delete": deleted_token.name}
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN)
