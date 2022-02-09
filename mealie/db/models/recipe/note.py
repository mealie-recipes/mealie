import sqlalchemy as sa

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


class Note(SqlAlchemyBase):
    __tablename__ = "notes"
    id = sa.Column(sa.Integer, primary_key=True)
    recipe_id = sa.Column(GUID, sa.ForeignKey("recipes.id"))
    title = sa.Column(sa.String)
    text = sa.Column(sa.String)

    def __init__(self, title, text) -> None:
        self.title = title
        self.text = text
