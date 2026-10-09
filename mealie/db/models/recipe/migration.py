import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


class RecipeMigrationModel(SqlAlchemyBase):
    """Original import identity, retained even when users edit the recipe."""

    __tablename__ = "recipe_migrations"
    __table_args__ = (sa.UniqueConstraint("household_id", "source", "fingerprint", name="uq_recipe_migration_source"),)

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    household_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    fingerprint: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    recipe_id: Mapped[GUID] = mapped_column(
        GUID, sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True
    )
