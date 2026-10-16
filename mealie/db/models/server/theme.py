from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID


class AppThemeModel(SqlAlchemyBase, BaseMixins):
    # Instance-wide singleton: at most one row is ever created. Unset columns fall back
    # to the THEME_* environment-variable defaults at the API layer, not here.
    __tablename__ = "app_theme"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    light_primary: Mapped[str | None] = mapped_column(String)
    light_accent: Mapped[str | None] = mapped_column(String)
    light_secondary: Mapped[str | None] = mapped_column(String)
    light_success: Mapped[str | None] = mapped_column(String)
    light_info: Mapped[str | None] = mapped_column(String)
    light_warning: Mapped[str | None] = mapped_column(String)
    light_error: Mapped[str | None] = mapped_column(String)

    dark_primary: Mapped[str | None] = mapped_column(String)
    dark_accent: Mapped[str | None] = mapped_column(String)
    dark_secondary: Mapped[str | None] = mapped_column(String)
    dark_success: Mapped[str | None] = mapped_column(String)
    dark_info: Mapped[str | None] = mapped_column(String)
    dark_warning: Mapped[str | None] = mapped_column(String)
    dark_error: Mapped[str | None] = mapped_column(String)

    # Non-color "look and feel" - corner roundedness and whether cards cast a shadow.
    # Applied as CSS custom properties rather than per-component Vuetify props, so one value
    # consistently reaches every card/button/input without touching every component.
    border_radius: Mapped[str | None] = mapped_column(String)
    card_style: Mapped[str | None] = mapped_column(String)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
