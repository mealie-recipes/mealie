import sqlalchemy as sa
from mealie.db.models.model_base import SqlAlchemyBase


class Tool(SqlAlchemyBase):
    __tablename__ = "tools"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("recipes.id"))
    tool = sa.Column(sa.String)

    def __init__(self, tool) -> None:
        self.tool = tool
