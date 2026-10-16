from pydantic_settings import BaseSettings, SettingsConfigDict


class Theme(BaseSettings):
    light_primary: str = "#A65F1B"
    light_accent: str = "#007A99"
    light_secondary: str = "#973542"
    light_success: str = "#43A047"
    light_info: str = "#1976D2"
    light_warning: str = "#FF6D00"
    light_error: str = "#EF5350"

    dark_primary: str = "#A65F1B"
    dark_accent: str = "#007A99"
    dark_secondary: str = "#973542"
    dark_success: str = "#43A047"
    dark_info: str = "#1976D2"
    dark_warning: str = "#FF6D00"
    dark_error: str = "#EF5350"

    border_radius: str = "soft"
    card_style: str = "elevated"
    model_config = SettingsConfigDict(env_prefix="theme_", extra="allow")
