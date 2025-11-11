from typing import ClassVar, Self

from fastapi import Request, Response
from pydantic import BaseModel, Field, PrivateAttr, computed_field, field_validator

from ..config import get_app_settings


class MealieAuthToken(BaseModel):
    """
    Mealie authentication token model for managing access tokens and their associated cookie settings.

    Must pass the Request object to determine cookie attributes based on the request context.
    """

    TOKEN_KEY: ClassVar = "mealie.access_token"

    _request: Request = PrivateAttr()
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(None, validate_default=True)

    def __init__(self, request: Request, **data) -> None:
        super().__init__(**data)
        self._request = request

    @computed_field  # type: ignore
    @property
    def http_only(self) -> bool:
        return False  # to allow JS access for frontend

    @computed_field  # type: ignore
    @property
    def secure(self) -> bool:
        settings = get_app_settings()
        return settings.PRODUCTION

    @computed_field  # type: ignore
    @property
    def samesite(self) -> str | None:
        forwarded_proto = self._request.headers.get("x-forwarded-proto", "").lower()
        is_https = self._request.url.scheme == "https" or forwarded_proto == "https"

        if is_https and self.secure:
            return "none"
        else:
            return "lax"

    @field_validator("expires_in", mode="before")
    def validate_expires_in(cls, v):
        if isinstance(v, float):
            return int(v)
        if v is not None:
            return v

        settings = get_app_settings()
        return settings.TOKEN_TIME * 60 * 60

    def respond(self, response: Response) -> Self:
        """
        Sets the cookie on the response and returns self. For use in an API route.

        Usage: `return MealieAuthToken(...).respond(response)`
        """

        response.set_cookie(
            key=self.TOKEN_KEY,
            value=self.access_token,
            httponly=self.http_only,
            max_age=self.expires_in,
            secure=self.secure,
            samesite=self.samesite,
        )
        return self
