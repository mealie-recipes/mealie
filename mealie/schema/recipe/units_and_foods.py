from fastapi_camelcase import CamelModel


class CreateIngredientFood(CamelModel):
    name: str
    description: str = ""


class CreateIngredientUnit(CreateIngredientFood):
    abbreviation: str = ""


class IngredientFood(CreateIngredientFood):
    id: int

    class Config:
        orm_mode = True


class IngredientUnit(CreateIngredientUnit):
    id: int

    class Config:
        orm_mode = True
