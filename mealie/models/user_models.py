from pydantic import BaseModel


class CreateUser(BaseModel):
    full_name: str
    email: str
    password: str
    family: str

    class Config:
        schema_extra = {
            "full_name": "Change Me",
            "email": "changeme@email.com",
            "password": "MyPassword",
            "family": "public",
        }


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    family: str
