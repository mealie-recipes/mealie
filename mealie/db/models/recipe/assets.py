import sqlalchemy as sa
from mealie.db.models.model_base import SqlAlchemyBase


class RecipeAsset(SqlAlchemyBase):
    __tablename__ = "recipe_assets"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    name = sa.Column(sa.String)
    icon = sa.Column(sa.String)


    def __init__(
        self,
        name=None,
        icon=None,
    ) -> None:
        self.name = name
        self.icon = icon

