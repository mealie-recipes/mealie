import sqlalchemy as sa
from mealie.db.models.model_base import SqlAlchemyBase


class RecipeAsset(SqlAlchemyBase):
    __tablename__ = "recipe_assets"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("recipes.id"))
    name = sa.Column(sa.String)
    icon = sa.Column(sa.String)
    file_name = sa.Column(sa.String)

    def __init__(
        self,
        name=None,
        icon=None,
        file_name=None,
    ) -> None:
        self.name = name
        self.file_name = file_name
        self.icon = icon
