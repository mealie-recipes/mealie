from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init
from .._model_utils.guid import GUID


class RecipeTimelineEvent(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_timeline_events"
    id = Column(GUID, primary_key=True, default=GUID.generate)

    # Parent Recipe
    recipe_id = Column(GUID, ForeignKey("recipes.id"), nullable=False)
    recipe = relationship("RecipeModel", back_populates="timeline_events")

    # Related User (Actor)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="recipe_timeline_events", single_parent=True, foreign_keys=[user_id])

    # General Properties
    subject = Column(String, nullable=False)
    message = Column(String)
    event_type = Column(String)
    image = Column(String)

    # Timestamps
    timestamp = Column(DateTime)

    @auto_init()
    def __init__(
        self,
        timestamp=None,
        **_,
    ) -> None:
        self.timestamp = timestamp or datetime.now()
