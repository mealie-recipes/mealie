import sqlalchemy as sa

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


class RecipeAsset(SqlAlchemyBase):
    __tablename__ = "recipe_assets"
    id = sa.Column(sa.Integer, primary_key=True)
    recipe_id = sa.Column(GUID, sa.ForeignKey("recipes.id"))
    name = sa.Column(sa.String)
    icon = sa.Column(sa.String)
    file_name = sa.Column(sa.String)

    def __init__(self, name=None, icon=None, file_name=None) -> None:
        self.name = name
        self.file_name = file_name
        self.icon = icon
