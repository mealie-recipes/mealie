from fastapi_camelcase import CamelModel


class RecipeToolCreate(CamelModel):
    name: str
    on_hand: bool = False


class RecipeTool(RecipeToolCreate):
    id: int

    class Config:
        orm_mode = True
