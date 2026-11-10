from pydantic import BaseModel

# TODO: Should these exist?!?!?!?!?


class UpdateImageResponse(BaseModel):
    image: str


class RecipeDuplicate(BaseModel):
    name: str | None = None
