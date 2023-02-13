import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


class Note(SqlAlchemyBase):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    recipe_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("recipes.id"), index=True)
    title: Mapped[str | None] = mapped_column(sa.String)
    text: Mapped[str | None] = mapped_column(sa.String)

    def __init__(self, title, text) -> None:
        self.title = title
        self.text = text
