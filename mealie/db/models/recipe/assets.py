import sqlalchemy as sa
from sqlalchemy.orm import mapped_column

from mealie.db.models._model_base import FilterableColumn, SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


class RecipeAsset(SqlAlchemyBase):
    __tablename__ = "recipe_assets"
    id: FilterableColumn[int] = mapped_column(sa.Integer, primary_key=True)
    recipe_id: FilterableColumn[GUID | None] = mapped_column(GUID, sa.ForeignKey("recipes.id"), index=True)
    name: FilterableColumn[str | None] = mapped_column(sa.String)
    icon: FilterableColumn[str | None] = mapped_column(sa.String)
    file_name: FilterableColumn[str | None] = mapped_column(sa.String)

    def __init__(self, name=None, icon=None, file_name=None) -> None:
        self.name = name
        self.file_name = file_name
        self.icon = icon
