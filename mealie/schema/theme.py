from typing import Optional

from pydantic import BaseModel


class Colors(BaseModel):
    primary: str = "#E58325"
    accent: str = "#00457A"
    secondary: str = "#973542"
    success: str = "#43A047"
    info: str = "#4990BA"
    warning: str = "#FF4081"
    error: str = "#EF5350"

    class Config:
        orm_mode = True


class SiteTheme(BaseModel):
    id: Optional[int]
    name: str = "default"
    colors: Colors = Colors()

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "default",
                "colors": {
                    "primary": "#E58325",
                    "accent": "#00457A",
                    "secondary": "#973542",
                    "success": "#5AB1BB",
                    "info": "#4990BA",
                    "warning": "#FF4081",
                    "error": "#EF5350",
                },
            }
        }
