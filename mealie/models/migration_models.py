from pydantic.main import BaseModel


class ChowdownURL(BaseModel):
    url: str

    class Config:
        schema_extra = {
            "example": {
                "url": "https://chowdownrepo.com/repo",
            }
        }
