from datetime import UTC, datetime, timedelta

import jwt

from mealie.core.config import get_app_settings

ALGORITHM = "HS256"
ISS = "mealie"


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> tuple[str, timedelta]:
    """Signs a JWT, returning it alongside the lifetime it was granted.

    Callers need the lifetime to tell the client when to refresh, so it is returned rather than left
    for the client to recover by decoding the token itself.
    """
    settings = get_app_settings()

    expires_delta = expires_delta or timedelta(hours=settings.TOKEN_TIME)
    issued_at = datetime.now(UTC)

    to_encode = data.copy()
    to_encode["iss"] = ISS
    to_encode["iat"] = issued_at
    to_encode["exp"] = issued_at + expires_delta

    return jwt.encode(to_encode, settings.SECRET, algorithm=ALGORITHM), expires_delta
