from typing import Optional

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
