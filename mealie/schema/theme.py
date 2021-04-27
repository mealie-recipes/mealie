from pydantic import BaseModel


class Colors(BaseModel):
    primary: str = "#E58325"
    accent: str = "#00457A"
    secondary: str = "#973542"
    success: str = "#4CAF50"
    info: str = "#4990BA"
    warning: str = "#FF4081"
    error: str = "#EF5350"

    class Config:
        orm_mode = True


class SiteTheme(BaseModel):
    name: str = "default"
    colors: Colors = Colors()

    class Config:
        orm_mode = True
