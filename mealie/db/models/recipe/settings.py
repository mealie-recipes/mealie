import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


class RecipeSettings(SqlAlchemyBase):
    __tablename__ = "recipe_settings"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    recipe_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("recipes.id"), index=True)
    public: Mapped[bool | None] = mapped_column(sa.Boolean)
    show_nutrition: Mapped[bool | None] = mapped_column(sa.Boolean)
    show_assets: Mapped[bool | None] = mapped_column(sa.Boolean)
    landscape_view: Mapped[bool | None] = mapped_column(sa.Boolean)
    disable_amount: Mapped[bool | None] = mapped_column(sa.Boolean, default=True)
    disable_comments: Mapped[bool | None] = mapped_column(sa.Boolean, default=False)
    locked: Mapped[bool | None] = mapped_column(sa.Boolean, default=False)

    def __init__(
        self,
        public=True,
        show_nutrition=True,
        show_assets=True,
        landscape_view=True,
        disable_amount=True,
        disable_comments=False,
        locked=False,
    ) -> None:
        self.locked = locked
        self.public = public
        self.show_nutrition = show_nutrition
        self.show_assets = show_assets
        self.landscape_view = landscape_view
        self.disable_amount = disable_amount
        self.disable_comments = disable_comments
