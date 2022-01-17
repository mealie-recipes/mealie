from sqlalchemy import Boolean, Column, ForeignKey, String, orm

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import GUID, auto_init


class GroupEventNotifierOptionsModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_events_notifier_options"

    id = Column(GUID, primary_key=True, default=GUID.generate)
    event_notifier_id = Column(GUID, ForeignKey("group_events_notifiers.id"), nullable=False)

    recipe_created = Column(Boolean, default=False, nullable=False)
    recipe_updated = Column(Boolean, default=False, nullable=False)
    recipe_deleted = Column(Boolean, default=False, nullable=False)

    user_signup = Column(Boolean, default=False, nullable=False)

    data_migrations = Column(Boolean, default=False, nullable=False)
    data_export = Column(Boolean, default=False, nullable=False)
    data_import = Column(Boolean, default=False, nullable=False)

    mealplan_entry_created = Column(Boolean, default=False, nullable=False)

    shopping_list_created = Column(Boolean, default=False, nullable=False)
    shopping_list_updated = Column(Boolean, default=False, nullable=False)
    shopping_list_deleted = Column(Boolean, default=False, nullable=False)

    cookbook_created = Column(Boolean, default=False, nullable=False)
    cookbook_updated = Column(Boolean, default=False, nullable=False)
    cookbook_deleted = Column(Boolean, default=False, nullable=False)

    tag_created = Column(Boolean, default=False, nullable=False)
    tag_updated = Column(Boolean, default=False, nullable=False)
    tag_deleted = Column(Boolean, default=False, nullable=False)

    category_created = Column(Boolean, default=False, nullable=False)
    category_updated = Column(Boolean, default=False, nullable=False)
    category_deleted = Column(Boolean, default=False, nullable=False)

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class GroupEventNotifierModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_events_notifiers"

    id = Column(GUID, primary_key=True, default=GUID.generate)
    name = Column(String, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    apprise_url = Column(String, nullable=False)

    group = orm.relationship("Group", back_populates="group_event_notifiers", single_parent=True)
    group_id = Column(GUID, ForeignKey("groups.id"), index=True)

    options = orm.relationship(GroupEventNotifierOptionsModel, uselist=False, cascade="all, delete-orphan")

    @auto_init()
    def __init__(self, **_) -> None:
        pass
