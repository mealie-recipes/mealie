from enum import StrEnum

from pydantic import BaseModel

from mealie.schema._mealie import MealieModel


class CreateBackupResponse(BaseModel):
    message: str
    error: bool = False
    duplicate: bool = False
    duplicateOf: str | None = None

    @classmethod
    def respond(cls, message: str, duplicate: bool = False, duplicateOf: str | None = None) -> "CreateBackupResponse":
        return cls(message=message, duplicate=duplicate, duplicateOf=duplicateOf)


class ErrorResponse(BaseModel):
    message: str
    error: bool = True
    exception: str | None = None

    @classmethod
    def respond(cls, message: str, exception: str | None = None) -> dict:
        """
        This method is an helper to create an object and convert to a dictionary
        in the same call, for use while providing details to a HTTPException
        """
        return cls(message=message, exception=exception).model_dump()


class SuccessResponse(BaseModel):
    message: str
    error: bool = False

    @classmethod
    def respond(cls, message: str = "") -> dict:
        """
        This method is an helper to create an object and convert to a dictionary
        in the same call, for use while providing details to a HTTPException
        """
        return cls(message=message).model_dump()


class FileTokenResponse(MealieModel):
    file_token: str

    @classmethod
    def respond(cls, token: str) -> dict:
        """
        This method is an helper to create an object and convert to a dictionary
        in the same call, for use while providing details to a HTTPException
        """
        return cls(file_token=token).model_dump()


class SSEDataEventStatus(StrEnum):
    PROGRESS = "progress"
    DONE = "done"
    ERROR = "error"


class SSEDataEventBase(BaseModel): ...


class SSEDataEventMessage(SSEDataEventBase):
    message: str


class SSEDataEventDone(SSEDataEventBase):
    slug: str
