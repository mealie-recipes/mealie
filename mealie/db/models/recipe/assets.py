import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


class RecipeAsset(SqlAlchemyBase):
    __tablename__ = "recipe_assets"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    recipe_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("recipes.id"), index=True)
    name: Mapped[str | None] = mapped_column(sa.String)
    icon: Mapped[str | None] = mapped_column(sa.String)
    file_name: Mapped[str | None] = mapped_column(sa.String)

    def __init__(self, name=None, icon=None, file_name=None) -> None:
        self.name = name
        self.file_name = file_name
        self.icon = icon
