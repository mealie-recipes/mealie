from typing import Optional

from fastapi_camelcase import CamelModel


class Nutrition(CamelModel):
    calories: Optional[str]
    fat_content: Optional[str]
    protein_content: Optional[str]
    carbohydrate_content: Optional[str]
    fiber_content: Optional[str]
    sodium_content: Optional[str]
    sugar_content: Optional[str]

    class Config:
        orm_mode = True
