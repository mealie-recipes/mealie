import sqlalchemy as sa

from mealie.db.models._model_base import SqlAlchemyBase


class ApiExtras(SqlAlchemyBase):
    __tablename__ = "api_extras"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("recipes.id"))
    key_name = sa.Column(sa.String)
    value = sa.Column(sa.String)

    def __init__(self, key, value) -> None:
        self.key_name = key
        self.value = value
