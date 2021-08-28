from datetime import timedelta

from fastapi import HTTPException, status
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session

from mealie.core.security import create_access_token
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.core.dependencies import get_current_user
from mealie.routes.routers import UserAPIRouter
from mealie.schema.user import CreateToken, LoingLiveTokenIn, LongLiveTokenInDB, UserInDB

router = UserAPIRouter()


@router.post("/api-tokens", status_code=status.HTTP_201_CREATED)
async def create_api_token(
    token_name: LoingLiveTokenIn,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Create api_token in the Database """

    token_data = {"long_token": True, "id": current_user.id}

    five_years = timedelta(1825)
    token = create_access_token(token_data, five_years)

    token_model = CreateToken(
        name=token_name.name,
        token=token,
        parent_id=current_user.id,
    )

    new_token_in_db = db.api_tokens.create(session, token_model)

    if new_token_in_db:
        return {"token": token}


@router.delete("/api-tokens/{token_id}")
async def delete_api_token(
    token_id: int,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Delete api_token from the Database """
    token: LongLiveTokenInDB = db.api_tokens.get(session, token_id)

    if not token:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Could not locate token with id '{token_id}' in database")

    if token.user.email == current_user.email:
        deleted_token = db.api_tokens.delete(session, token_id)
        return {"token_delete": deleted_token.name}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
