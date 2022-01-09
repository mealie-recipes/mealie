from sqlalchemy import Boolean, Column, ForeignKey, String, orm

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import GUID, auto_init


class GroupEventNotifierOptionsModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_events_notifier_options"

    id = Column(GUID, primary_key=True, default=GUID.generate)
    event_notifier_id = Column(GUID, ForeignKey("group_events_notifiers.id"), nullable=False)

    recipe_create = Column(Boolean, default=False, nullable=False)
    recipe_update = Column(Boolean, default=False, nullable=False)
    recipe_delete = Column(Boolean, default=False, nullable=False)

    user_signup = Column(Boolean, default=False, nullable=False)

    data_migrations = Column(Boolean, default=False, nullable=False)
    data_export = Column(Boolean, default=False, nullable=False)
    data_import = Column(Boolean, default=False, nullable=False)

    new_mealplan_entry = Column(Boolean, default=False, nullable=False)

    shopping_list_create = Column(Boolean, default=False, nullable=False)
    shopping_list_update = Column(Boolean, default=False, nullable=False)
    shopping_list_delete = Column(Boolean, default=False, nullable=False)

    cookbook_create = Column(Boolean, default=False, nullable=False)
    cookbook_update = Column(Boolean, default=False, nullable=False)
    cookbook_delete = Column(Boolean, default=False, nullable=False)

    tag_create = Column(Boolean, default=False, nullable=False)
    tag_update = Column(Boolean, default=False, nullable=False)
    tag_delete = Column(Boolean, default=False, nullable=False)

    category_create = Column(Boolean, default=False, nullable=False)
    category_update = Column(Boolean, default=False, nullable=False)
    category_delete = Column(Boolean, default=False, nullable=False)

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class GroupEventNotifierModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_events_notifiers"

    id = Column(GUID, primary_key=True, default=GUID.generate)
    name = Column(String, nullable=False)
    enabled = Column(String, default=True, nullable=False)
    apprise_url = Column(String, nullable=False)

    group = orm.relationship("Group", back_populates="group_event_notifiers", single_parent=True)
    group_id = Column(GUID, ForeignKey("groups.id"), index=True)

    options = orm.relationship(GroupEventNotifierOptionsModel, uselist=False, cascade="all, delete-orphan")

    @auto_init()
    def __init__(self, **_) -> None:
        pass
