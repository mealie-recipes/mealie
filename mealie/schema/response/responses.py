from pydantic import BaseModel

from mealie.schema._mealie import MealieModel


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
