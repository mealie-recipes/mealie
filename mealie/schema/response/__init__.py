from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str
    error: bool = True
    exception: str = None
