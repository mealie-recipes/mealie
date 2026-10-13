from pydantic_settings import BaseSettings, SettingsConfigDict


class Theme(BaseSettings):
    light_primary: str = "#C4502A"
    light_accent: str = "#007A99"
    light_secondary: str = "#973542"
    light_success: str = "#2A7531"
    light_info: str = "#1565C0"
    light_warning: str = "#A84B0A"
    light_error: str = "#B3261E"

    dark_primary: str = "#E0683C"
    dark_accent: str = "#007A99"
    dark_secondary: str = "#E08A73"
    dark_success: str = "#4CAF50"
    dark_info: str = "#5E9BD1"
    dark_warning: str = "#FF6D00"
    dark_error: str = "#F2706C"
    model_config = SettingsConfigDict(env_prefix="theme_", extra="allow")
