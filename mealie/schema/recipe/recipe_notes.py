from pydantic import BaseModel, ConfigDict


class RecipeNote(BaseModel):
    title: str
    text: str
    model_config = ConfigDict(from_attributes=True)
