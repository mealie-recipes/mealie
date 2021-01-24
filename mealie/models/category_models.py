from pydantic.main import BaseModel

class Category(BaseModel):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Breakfast"
            }
        }