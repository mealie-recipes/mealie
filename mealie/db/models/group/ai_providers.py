from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from .group import Group


def unwrap_headers_and_params(func):
    """Decorator function to unpack headers and params into dicts"""

    def unwrap(value: dict | None) -> list[dict]:
        if value is None:
            value = {}

        return [{"key": k, "value": v} for k, v in value.items()]

    def wrapper(*args, **kwargs):
        headers = kwargs.pop("request_headers", {})
        params = kwargs.pop("request_params", {})

        return func(
            *args,
            request_headers=unwrap(headers),
            request_params=unwrap(params),
            **kwargs,
        )

    return wrapper


class AIProviderKV:
    """
    Template for key-value pairs

    This class is not an actual table, so it does not inherit from SqlAlchemyBase
    """

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    key_name: orm.Mapped[str | None] = orm.mapped_column(sa.String)
    value: orm.Mapped[str | None] = orm.mapped_column(sa.String)

    def __init__(self, key, value) -> None:
        self.key_name = key
        self.value = value


class AIProviderHeaders(AIProviderKV, SqlAlchemyBase):
    __tablename__ = "ai_provider_headers"
    provider_id: orm.Mapped[GUID] = orm.mapped_column(GUID, sa.ForeignKey("ai_providers.id"), index=True)


class AIProviderParams(AIProviderKV, SqlAlchemyBase):
    __tablename__ = "ai_provider_params"
    provider_id: orm.Mapped[GUID] = orm.mapped_column(GUID, sa.ForeignKey("ai_providers.id"), index=True)


class AIProvider(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ai_providers"
    __table_args__ = (sa.UniqueConstraint("name", "settings_id", name="ai_providers_name_settings_id_key"),)
    id: orm.Mapped[GUID] = orm.mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: AssociationProxy[GUID] = association_proxy("settings", "group_id")

    settings_id: orm.Mapped[GUID] = orm.mapped_column(
        GUID, sa.ForeignKey("ai_provider_settings.id"), nullable=False, index=True
    )
    settings: orm.Mapped["AIProviderSettings"] = orm.relationship(
        "AIProviderSettings", foreign_keys="[AIProvider.settings_id]", back_populates="providers"
    )

    name: orm.Mapped[str] = orm.mapped_column(sa.String, index=True, nullable=False)
    base_url: orm.Mapped[str | None] = orm.mapped_column(sa.String, nullable=True)
    api_key: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    model: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    timeout: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=False, default=300)

    request_headers: orm.Mapped[list[AIProviderHeaders]] = orm.relationship(
        "AIProviderHeaders", cascade="all, delete-orphan"
    )
    request_params: orm.Mapped[list[AIProviderParams]] = orm.relationship(
        "AIProviderParams", cascade="all, delete-orphan"
    )

    @unwrap_headers_and_params
    @auto_init()
    def __init__(self, **_) -> None:
        pass


class AIProviderSettings(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ai_provider_settings"
    __table_args__ = (sa.UniqueConstraint("group_id", name="ai_provider_settings_group_id_key"),)
    id: orm.Mapped[GUID] = orm.mapped_column(GUID, primary_key=True, default=GUID.generate)

    group_id: orm.Mapped[GUID] = orm.mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group: orm.Mapped["Group"] = orm.relationship("Group", back_populates="ai_provider_settings")
    providers: orm.Mapped[list[AIProvider]] = orm.relationship(
        AIProvider,
        foreign_keys="[AIProvider.settings_id]",
        back_populates="settings",
        uselist=True,
        single_parent=True,
        cascade="all, delete-orphan",
    )

    # Configured Providers
    default_provider_id: orm.Mapped[GUID | None] = orm.mapped_column(
        GUID, sa.ForeignKey("ai_providers.id", use_alter=True), nullable=True, index=True
    )
    default_provider: orm.Mapped[AIProvider | None] = orm.relationship(
        AIProvider,
        foreign_keys="[AIProviderSettings.default_provider_id]",
        uselist=False,
        post_update=True,
    )

    audio_provider_id: orm.Mapped[GUID | None] = orm.mapped_column(
        GUID, sa.ForeignKey("ai_providers.id", use_alter=True), nullable=True, index=True
    )
    audio_provider: orm.Mapped[AIProvider | None] = orm.relationship(
        AIProvider,
        foreign_keys="[AIProviderSettings.audio_provider_id]",
        uselist=False,
        post_update=True,
    )

    image_provider_id: orm.Mapped[GUID | None] = orm.mapped_column(
        GUID, sa.ForeignKey("ai_providers.id", use_alter=True), nullable=True, index=True
    )
    image_provider: orm.Mapped[AIProvider | None] = orm.relationship(
        AIProvider,
        foreign_keys="[AIProviderSettings.image_provider_id]",
        uselist=False,
        post_update=True,
    )

    @auto_init()
    def __init__(self, **_) -> None:
        pass
