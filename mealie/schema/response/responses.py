from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str
    error: bool = True
    exception: Optional[str] = None

    @classmethod
    def respond(cls, message: str, exception: Optional[str] = None) -> dict:
        """
        This method is an helper to create an obect and convert to a dictionary
        in the same call, for use while providing details to a HTTPException
        """
        return cls(message=message, exception=exception).dict()


class SuccessResponse(BaseModel):
    message: str
    error: bool = False

    @classmethod
    def respond(cls, message: str) -> dict:
        """
        This method is an helper to create an obect and convert to a dictionary
        in the same call, for use while providing details to a HTTPException
        """
        return cls(message=message).dict()


class FileTokenResponse(CamelModel):
    file_token: str

    @classmethod
    def respond(cls, token: str) -> dict:
        """
        This method is an helper to create an obect and convert to a dictionary
        in the same call, for use while providing details to a HTTPException
        """
        return cls(file_token=token).dict()
