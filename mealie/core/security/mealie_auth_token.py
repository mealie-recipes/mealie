from typing import Self

from fastapi import Request, Response
from pydantic import BaseModel, Field, computed_field, field_validator

from ..config import get_app_settings


class MealieAuthToken(BaseModel):
    TOKEN_KEY = "mealie.access_token"

    request: Request = Field(exclude=True)

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(None, validate_default=True)

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
        forwarded_proto = self.request.headers.get("x-forwarded-proto", "").lower()
        is_https = self.request.url.scheme == "https" or forwarded_proto == "https"

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
