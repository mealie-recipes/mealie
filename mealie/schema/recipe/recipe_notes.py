from pydantic import ConfigDict, BaseModel


class RecipeNote(BaseModel):
    title: str
    text: str
    model_config = ConfigDict(from_attributes=True)
