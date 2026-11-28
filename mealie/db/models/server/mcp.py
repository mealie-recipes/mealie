from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


class McpSetting(SqlAlchemyBase):
    __tablename__ = "mcp_settings"

    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class McpClient(SqlAlchemyBase):
    __tablename__ = "mcp_clients"

    client_id: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False, index=True)
    client_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False)


class McpGrant(SqlAlchemyBase):
    __tablename__ = "mcp_grants"

    user_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    household_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(2048), nullable=False)
    scopes_json: Mapped[str] = mapped_column(Text, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class McpAuthorizationRequest(SqlAlchemyBase):
    __tablename__ = "mcp_authorization_requests"

    request_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    client_id: Mapped[str] = mapped_column(String(2048), nullable=False)
    params_json: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class McpAuthorizationCode(SqlAlchemyBase):
    __tablename__ = "mcp_authorization_codes"

    code_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    grant_id: Mapped[int] = mapped_column(Integer, ForeignKey("mcp_grants.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(2048), nullable=False)
    params_json: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class McpToken(SqlAlchemyBase):
    __tablename__ = "mcp_tokens"

    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    grant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("mcp_grants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    family_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(8), nullable=False)
    scopes_json: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
