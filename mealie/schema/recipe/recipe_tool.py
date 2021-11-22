from fastapi_camelcase import CamelModel


class RecipeToolCreate(CamelModel):
    name: str


class RecipeTool(RecipeToolCreate):
    id: int

    class Config:
        orm_mode = True
