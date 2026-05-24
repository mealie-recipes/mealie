"""add table for ai providers

Revision ID: 2187537c52b8
Revises: c7427796f7b6
Create Date: 2026-05-18 16:27:05.770218

"""

import sqlalchemy as sa
from alembic import op
from pydantic_settings import BaseSettings, SettingsConfigDict

import mealie.db.migration_types
from mealie.core.config import ENV
from mealie.core.root_logger import get_logger
from mealie.core.settings.settings import get_secrets_dir
from mealie.db.models._model_utils.guid import GUID

# revision identifiers, used by Alembic.
revision = "2187537c52b8"
down_revision: str | None = "c7427796f7b6"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None

logger = get_logger()


class LegacyOpenAISettings(BaseSettings):
    OPENAI_BASE_URL: str | None = None
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_AUDIO_MODEL: str = "whisper-1"
    OPENAI_CUSTOM_HEADERS: dict[str, str] = {}
    OPENAI_CUSTOM_PARAMS: dict[str, str] = {}
    OPENAI_ENABLE_IMAGE_SERVICES: bool = True
    OPENAI_ENABLE_TRANSCRIPTION_SERVICES: bool = True
    OPENAI_REQUEST_TIMEOUT: int = 300

    model_config = SettingsConfigDict(extra="ignore")


def get_openai_settings() -> LegacyOpenAISettings:

    return LegacyOpenAISettings(
        _env_file=ENV,
        _env_file_encoding="utf-8",
        _secrets_dir=get_secrets_dir(),
    )


def is_postgres() -> bool:
    return op.get_context().dialect.name == "postgresql"


def generate_id() -> str:
    val = GUID.generate()
    dialect = op.get_bind().dialect

    return GUID.convert_value_to_guid(val, dialect)  # type: ignore


def create_provider(settings_id: str, provider_id: str, model: str, openai_settings: LegacyOpenAISettings) -> None:
    logger.info(f"Creating provider '{model}'")

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "INSERT INTO ai_providers (id, settings_id, name, base_url, api_key, model, timeout) "
            "VALUES (:id, :settings_id, :name, :base_url, :api_key, :model, :timeout)"
        ),
        {
            "id": provider_id,
            "settings_id": settings_id,
            # we only create one provider per model in this mirgration script,
            # so there's no chance for collisions
            "name": model,
            "base_url": openai_settings.OPENAI_BASE_URL,
            "api_key": openai_settings.OPENAI_API_KEY,
            "model": model,
            "timeout": openai_settings.OPENAI_REQUEST_TIMEOUT,
        },
    )

    for key, value in openai_settings.OPENAI_CUSTOM_HEADERS.items():
        conn.execute(
            sa.text(
                "INSERT INTO ai_provider_headers (provider_id, key_name, value) "
                "VALUES (:provider_id, :key_name, :value)"
            ),
            {"provider_id": provider_id, "key_name": key, "value": value},
        )

    for key, value in openai_settings.OPENAI_CUSTOM_PARAMS.items():
        conn.execute(
            sa.text(
                "INSERT INTO ai_provider_params (provider_id, key_name, value) VALUES (:provider_id, :key_name, :value)"
            ),
            {"provider_id": provider_id, "key_name": key, "value": value},
        )


def create_providers() -> None:
    """Create provider settings and migrate legacy OPEN_AI_... environment variables to a provider"""

    openai_settings = get_openai_settings()
    create_providers = bool(openai_settings.OPENAI_API_KEY and openai_settings.OPENAI_MODEL)

    if create_providers:
        logger.info("Found legacy OpenAI configuration, creating new AI providers")

    conn = op.get_bind()
    groups = conn.execute(sa.text("SELECT id FROM groups")).fetchall()
    for (group_id,) in groups:
        logger.info(f"Creating provider settings for {group_id=}")

        # Create AI provider settings
        settings_id = generate_id()
        conn.execute(
            sa.text("INSERT INTO ai_provider_settings (id, group_id) VALUES (:id, :group_id)"),
            {"id": settings_id, "group_id": group_id},
        )

        if not create_providers:
            continue

        # Create provider
        default_provider_id = generate_id()
        model = openai_settings.OPENAI_MODEL
        create_provider(settings_id, default_provider_id, model, openai_settings)

        # Set the image provider if image services are enabled
        if openai_settings.OPENAI_ENABLE_IMAGE_SERVICES:
            image_provider_id = default_provider_id
        else:
            image_provider_id = None

        # Set the audio provider if transcription services are enabled
        if openai_settings.OPENAI_ENABLE_TRANSCRIPTION_SERVICES:
            transcription_model = openai_settings.OPENAI_AUDIO_MODEL or model
            if transcription_model == openai_settings.OPENAI_MODEL:
                audio_provider_id = default_provider_id
            else:
                # The transcription model is different than the base model, so create a new provider
                audio_provider_id = generate_id()
                create_provider(settings_id, audio_provider_id, transcription_model, openai_settings)
        else:
            audio_provider_id = None

        # Update the provider settings to reference new provider(s)
        conn.execute(
            sa.text(
                """
                UPDATE ai_provider_settings
                SET
                    default_provider_id = :default_provider_id,
                    audio_provider_id = :audio_provider_id,
                    image_provider_id = :image_provider_id
                WHERE id = :id
                """
            ),
            {
                "default_provider_id": default_provider_id,
                "audio_provider_id": audio_provider_id,
                "image_provider_id": image_provider_id,
                "id": settings_id,
            },
        )


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ai_provider_settings",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("default_provider_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("audio_provider_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("image_provider_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("created_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.Column("update_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.ForeignKeyConstraint(["default_provider_id"], ["ai_providers.id"], use_alter=True),
        sa.ForeignKeyConstraint(["audio_provider_id"], ["ai_providers.id"], use_alter=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(["image_provider_id"], ["ai_providers.id"], use_alter=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_id", name="ai_provider_settings_group_id_key"),
    )
    with op.batch_alter_table("ai_provider_settings", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_ai_provider_settings_default_provider_id"), ["default_provider_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_ai_provider_settings_audio_provider_id"), ["audio_provider_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_ai_provider_settings_created_at"), ["created_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_ai_provider_settings_group_id"), ["group_id"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_ai_provider_settings_image_provider_id"), ["image_provider_id"], unique=False
        )

    op.create_table(
        "ai_providers",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("settings_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("base_url", sa.String(), nullable=True),
        sa.Column("api_key", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("timeout", sa.Integer(), nullable=False),
        sa.Column("created_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.Column("update_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["settings_id"],
            ["ai_provider_settings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "settings_id", name="ai_providers_name_settings_id_key"),
    )
    with op.batch_alter_table("ai_providers", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_ai_providers_created_at"), ["created_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_ai_providers_name"), ["name"], unique=False)
        batch_op.create_index(batch_op.f("ix_ai_providers_settings_id"), ["settings_id"], unique=False)

    op.create_table(
        "ai_provider_headers",
        sa.Column("provider_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key_name", sa.String(), nullable=True),
        sa.Column("value", sa.String(), nullable=True),
        sa.Column("created_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.Column("update_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["ai_providers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("ai_provider_headers", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_ai_provider_headers_created_at"), ["created_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_ai_provider_headers_provider_id"), ["provider_id"], unique=False)

    op.create_table(
        "ai_provider_params",
        sa.Column("provider_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key_name", sa.String(), nullable=True),
        sa.Column("value", sa.String(), nullable=True),
        sa.Column("created_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.Column("update_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["ai_providers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("ai_provider_params", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_ai_provider_params_created_at"), ["created_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_ai_provider_params_provider_id"), ["provider_id"], unique=False)

    # ### end Alembic commands ###

    try:
        with op.get_bind().begin_nested():
            create_providers()
    except Exception:
        logger.exception("Failed to migrate legacy OpenAI config")


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("ai_provider_params", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_ai_provider_params_provider_id"))
        batch_op.drop_index(batch_op.f("ix_ai_provider_params_created_at"))

    op.drop_table("ai_provider_params")
    with op.batch_alter_table("ai_provider_headers", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_ai_provider_headers_provider_id"))
        batch_op.drop_index(batch_op.f("ix_ai_provider_headers_created_at"))

    op.drop_table("ai_provider_headers")
    with op.batch_alter_table("ai_providers", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_ai_providers_settings_id"))
        batch_op.drop_index(batch_op.f("ix_ai_providers_name"))
        batch_op.drop_index(batch_op.f("ix_ai_providers_created_at"))

    op.drop_table("ai_providers")
    with op.batch_alter_table("ai_provider_settings", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_ai_provider_settings_image_provider_id"))
        batch_op.drop_index(batch_op.f("ix_ai_provider_settings_group_id"))
        batch_op.drop_index(batch_op.f("ix_ai_provider_settings_created_at"))
        batch_op.drop_index(batch_op.f("ix_ai_provider_settings_audio_provider_id"))
        batch_op.drop_index(batch_op.f("ix_ai_provider_settings_default_provider_id"))

    op.drop_table("ai_provider_settings")
    # ### end Alembic commands ###
