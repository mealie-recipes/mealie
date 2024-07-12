from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, orm
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..group import Group
    from .household import Household


class GroupEventNotifierOptionsModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_events_notifier_options"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    event_notifier_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("group_events_notifiers.id"), nullable=False)

    recipe_created: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recipe_updated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recipe_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user_signup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    data_migrations: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_export: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_import: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    mealplan_entry_created: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    shopping_list_created: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    shopping_list_updated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    shopping_list_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    cookbook_created: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cookbook_updated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cookbook_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    tag_created: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tag_updated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tag_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    category_created: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    category_updated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    category_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class GroupEventNotifierModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_events_notifiers"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    name: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    apprise_url: Mapped[str] = mapped_column(String, nullable=False)

    group: Mapped[Optional["Group"]] = orm.relationship(
        "Group", back_populates="group_event_notifiers", single_parent=True
    )
    group_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("groups.id"), index=True)
    household: Mapped[Optional["Household"]] = orm.relationship(
        "Household", back_populates="group_event_notifiers", single_parent=True
    )
    household_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("households.id"), index=True)

    options: Mapped[GroupEventNotifierOptionsModel] = orm.relationship(
        GroupEventNotifierOptionsModel, uselist=False, cascade="all, delete-orphan"
    )

    @auto_init()
    def __init__(self, **_) -> None:
        pass
