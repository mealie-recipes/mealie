from pydantic import BaseModel

class Colors(BaseModel):
    primary: str
    accent: str
    secondary: str
    success: str
    info: str
    warning: str
    error: str


class SiteTheme(BaseModel):
    name: str
    colors: Colors

    class Config:
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