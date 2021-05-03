import sqlalchemy as sa
from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase


class Event(SqlAlchemyBase, BaseMixins):
    __tablename__ = "events"
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    text = sa.Column(sa.String)
    time_stamp = sa.Column(sa.DateTime)
    category = sa.Column(sa.String)

    def __init__(self, title, text, time_stamp, category, *args, **kwargs) -> None:
        self.title = title
        self.text = text
        self.time_stamp = time_stamp
        self.category = category
