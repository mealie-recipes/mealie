from ._base import OpenAIBase


class OpenAIIngredient(OpenAIBase):
    input: str
    confidence: float | None = None

    quantity: float | None = 0
    unit: str | None = None
    food: str | None = None
    note: str | None = None


class OpenAIIngredients(OpenAIBase):
    ingredients: list[OpenAIIngredient] = []
