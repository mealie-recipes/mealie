import sqlalchemy as sa
from mealie.db.models.model_base import SqlAlchemyBase


class RecipeSettings(SqlAlchemyBase):
    __tablename__ = "recipe_settings"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("recipes.id"))
    public = sa.Column(sa.Boolean)
    show_nutrition = sa.Column(sa.Boolean)
    show_assets = sa.Column(sa.Boolean)
    landscape_view = sa.Column(sa.Boolean)

    def __init__(self, public=True, show_nutrition=True, show_assets=True, landscape_view=True) -> None:
        self.public = public
        self.show_nutrition = show_nutrition
        self.show_assets = show_assets
        self.landscape_view = landscape_view
