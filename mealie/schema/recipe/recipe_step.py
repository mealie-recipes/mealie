from typing import Optional

from fastapi_camelcase import CamelModel


class RecipeStep(CamelModel):
    title: Optional[str] = ""
    text: str

    class Config:
        orm_mode = True
