from pydantic import BaseModel


class ValidationResponse(BaseModel):
    valid: bool = False
