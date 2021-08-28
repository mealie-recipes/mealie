from pydantic import BaseModel


class RecipeNote(BaseModel):
    title: str
    text: str

    class Config:
        orm_mode = True
