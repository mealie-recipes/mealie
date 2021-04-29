import sqlalchemy as sa
from mealie.db.models.model_base import SqlAlchemyBase


class Note(SqlAlchemyBase):
    __tablename__ = "notes"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("recipes.id"))
    title = sa.Column(sa.String)
    text = sa.Column(sa.String)

    def __init__(self, title, text) -> None:
        self.title = title
        self.text = text
