import enum

from pydantic import UUID4, ConfigDict

from mealie.schema._mealie import MealieModel


class ThemeBorderRadius(enum.StrEnum):
    sharp = "sharp"
    soft = "soft"
    round = "round"


class ThemeCardStyle(enum.StrEnum):
    elevated = "elevated"
    flat = "flat"


class ThemeFontFamily(enum.StrEnum):
    """System font stacks only - no webfont is ever downloaded, matching the rest of the app."""

    sans = "sans"
    rounded = "rounded"
    serif = "serif"
    mono = "mono"


class ThemeFontSize(enum.StrEnum):
    small = "small"
    medium = "medium"
    large = "large"


class AppStatistics(MealieModel):
    total_recipes: int
    total_users: int
    total_households: int
    total_groups: int
    uncategorized_recipes: int
    untagged_recipes: int


class AppInfo(MealieModel):
    production: bool
    version: str
    demo_status: bool
    allow_signup: bool
    allow_password_login: bool
    default_group_slug: str | None = None
    default_household_slug: str | None = None
    enable_oidc: bool
    oidc_redirect: bool
    oidc_provider_name: str
    enable_reverse_proxy_auth: bool
    token_time: int
    allowed_iframe_hosts: list[str] = []
    branding_name: str = "Mealie"
    branding_logo_url: str | None = None


class AppTheme(MealieModel):
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

    border_radius: ThemeBorderRadius = ThemeBorderRadius.soft
    card_style: ThemeCardStyle = ThemeCardStyle.elevated
    font_family: ThemeFontFamily = ThemeFontFamily.sans
    font_size: ThemeFontSize = ThemeFontSize.medium


class AppThemeOut(AppTheme):
    # The id of the single stored row, if an instance-wide override has been saved.
    # Internal to the admin theme repo/route - the public /app/about/theme endpoint
    # only ever serves the plain AppTheme shape.
    id: UUID4 | None = None
    model_config = ConfigDict(from_attributes=True)


class AppStartupInfo(MealieModel):
    is_first_login: bool
    """
    The applications best guess that a user hasn't logged in. Currently, it really
    on indicates that the 'changeme@example.com' user is still in the database. Once
    it is removed, this will always return False.
    """

    is_demo: bool


class AdminAboutInfo(AppInfo):
    versionLatest: str
    api_port: int
    api_docs: bool
    db_type: str
    db_url: str | None = None
    default_group: str
    default_household: str
    build_id: str
    recipe_scraper_version: str


class CheckAppConfig(MealieModel):
    email_ready: bool
    ldap_ready: bool
    ldap_disabled: bool
    oidc_ready: bool
    oidc_disabled: bool
    reverse_proxy_auth_ready: bool
    reverse_proxy_auth_disabled: bool
    base_url_set: bool
    is_up_to_date: bool
