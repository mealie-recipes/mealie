from typing import Optional

from fastapi_camelcase import CamelModel


class RecipeAsset(CamelModel):
    name: str
    icon: str
    file_name: Optional[str]

    class Config:
        orm_mode = True
