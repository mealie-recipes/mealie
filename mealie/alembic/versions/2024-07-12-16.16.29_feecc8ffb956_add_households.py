"""add households

Revision ID: feecc8ffb956
Revises: 32d69327997b
Create Date: 2024-07-12 16:16:29.973929

"""

from datetime import UTC, datetime
from textwrap import dedent
from typing import Any
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from slugify import slugify
from sqlalchemy import orm

import mealie.db.migration_types
from mealie.core.config import get_app_settings

# revision identifiers, used by Alembic.
revision = "feecc8ffb956"
down_revision = "32d69327997b"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None

settings = get_app_settings()


def is_postgres():
    return op.get_context().dialect.name == "postgresql"


def generate_id() -> str:
    """See GUID.convert_value_to_guid"""
    val = uuid4()
    if is_postgres():
        return str(val)
    else:
        return f"{val.int:032x}"


def dedupe_cookbook_slugs():
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    with session:
        sql = sa.text(
            dedent(
                """
                SELECT slug, group_id, COUNT(*)
                FROM cookbooks
                GROUP BY slug, group_id
                HAVING COUNT(*) > 1
                """
            )
        )
        rows = session.execute(sql).fetchall()

        for slug, group_id, _ in rows:
            sql = sa.text(
                dedent(
                    """
                    SELECT id
                    FROM cookbooks
                    WHERE slug = :slug AND group_id = :group_id
                    ORDER BY id
                    """
                )
            )
            cookbook_ids = session.execute(sql, {"slug": slug, "group_id": group_id}).fetchall()

            for i, (cookbook_id,) in enumerate(cookbook_ids):
                if i == 0:
                    continue

                sql = sa.text(
                    dedent(
                        """
                        UPDATE cookbooks
                        SET slug = :slug || '-' || :i
                        WHERE id = :id
                        """
                    )
                )
                session.execute(sql, {"slug": slug, "i": i, "id": cookbook_id})


def create_household(session: orm.Session, group_id: str) -> str:
    # create/insert household
    household_id = generate_id()
    timestamp = datetime.now(UTC).isoformat()
    household_data = {
        "id": household_id,
        "name": settings.DEFAULT_HOUSEHOLD,
        "slug": slugify(settings.DEFAULT_HOUSEHOLD),
        "group_id": group_id,
        "created_at": timestamp,
        "update_at": timestamp,
    }
    columns = ", ".join(household_data.keys())
    placeholders = ", ".join(f":{key}" for key in household_data.keys())
    sql_statement = f"INSERT INTO households ({columns}) VALUES ({placeholders})"

    session.execute(sa.text(sql_statement), household_data)

    # fetch group preferences so we can copy them over to household preferences
    migrated_field_defaults = {
        "private_group": True,  # this is renamed later
        "first_day_of_week": 0,
        "recipe_public": True,
        "recipe_show_nutrition": False,
        "recipe_show_assets": False,
        "recipe_landscape_view": False,
        "recipe_disable_comments": False,
        "recipe_disable_amount": True,
    }
    sql_statement = (
        f"SELECT {', '.join(migrated_field_defaults.keys())} FROM group_preferences WHERE group_id = :group_id"
    )
    group_preferences = session.execute(sa.text(sql_statement), {"group_id": group_id}).fetchone()

    # build preferences data
    if group_preferences:
        preferences_data: dict[str, Any] = {}
        for i, (field, default_value) in enumerate(migrated_field_defaults.items()):
            value = group_preferences[i]
            preferences_data[field] = value if value is not None else default_value
    else:
        preferences_data = migrated_field_defaults

    preferences_data["id"] = generate_id()
    preferences_data["household_id"] = household_id
    preferences_data["created_at"] = timestamp
    preferences_data["update_at"] = timestamp
    preferences_data["private_household"] = preferences_data.pop("private_group")

    # insert preferences data
    columns = ", ".join(preferences_data.keys())
    placeholders = ", ".join(f":{key}" for key in preferences_data.keys())
    sql_statement = f"INSERT INTO household_preferences ({columns}) VALUES ({placeholders})"

    session.execute(sa.text(sql_statement), preferences_data)

    return household_id


def create_households_for_groups() -> dict[str, str]:
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    group_id_household_id_map: dict[str, str] = {}
    with session:
        rows = session.execute(sa.text("SELECT id FROM groups")).fetchall()
        for row in rows:
            group_id = row[0]
            group_id_household_id_map[group_id] = create_household(session, group_id)

    return group_id_household_id_map


def _do_assignment(session: orm.Session, table: str, group_id: str, household_id: str):
    sql = sa.text(
        dedent(
            f"""
            UPDATE {table}
            SET household_id = :household_id
            WHERE group_id = :group_id
            """,
        )
    )
    session.execute(sql, {"group_id": group_id, "household_id": household_id})


def assign_households(group_id_household_id_map: dict[str, str]):
    tables = [
        "cookbooks",
        "group_events_notifiers",
        "group_meal_plan_rules",
        "invite_tokens",
        "recipe_actions",
        "users",
        "webhook_urls",
    ]

    bind = op.get_bind()
    session = orm.Session(bind=bind)
    with session:
        for table in tables:
            for group_id, household_id in group_id_household_id_map.items():
                _do_assignment(session, table, group_id, household_id)


def populate_household_data():
    group_id_household_id_map = create_households_for_groups()
    assign_households(group_id_household_id_map)


def upgrade():
    dedupe_cookbook_slugs()

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "households",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=True),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_id", "name", name="household_name_group_id_key"),
        sa.UniqueConstraint("group_id", "slug", name="household_slug_group_id_key"),
    )
    op.create_index(op.f("ix_households_created_at"), "households", ["created_at"], unique=False)
    op.create_index(op.f("ix_households_group_id"), "households", ["group_id"], unique=False)
    op.create_index(op.f("ix_households_name"), "households", ["name"], unique=False)
    op.create_index(op.f("ix_households_slug"), "households", ["slug"], unique=False)
    op.create_table(
        "household_preferences",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("private_household", sa.Boolean(), nullable=True),
        sa.Column("first_day_of_week", sa.Integer(), nullable=True),
        sa.Column("recipe_public", sa.Boolean(), nullable=True),
        sa.Column("recipe_show_nutrition", sa.Boolean(), nullable=True),
        sa.Column("recipe_show_assets", sa.Boolean(), nullable=True),
        sa.Column("recipe_landscape_view", sa.Boolean(), nullable=True),
        sa.Column("recipe_disable_comments", sa.Boolean(), nullable=True),
        sa.Column("recipe_disable_amount", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_household_preferences_created_at"), "household_preferences", ["created_at"], unique=False)
    op.create_index(
        op.f("ix_household_preferences_household_id"), "household_preferences", ["household_id"], unique=False
    )

    with op.batch_alter_table("cookbooks") as batch_op:
        batch_op.add_column(sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_index(op.f("ix_cookbooks_household_id"), ["household_id"], unique=False)
        batch_op.create_foreign_key("fk_cookbooks_household_id", "households", ["household_id"], ["id"])

        # not directly related to households, but important for frontend routes
        batch_op.create_unique_constraint("cookbook_slug_group_id_key", ["slug", "group_id"])

    with op.batch_alter_table("group_events_notifiers") as batch_op:
        batch_op.add_column(sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_index(op.f("ix_group_events_notifiers_household_id"), ["household_id"], unique=False)
        batch_op.create_foreign_key("fk_group_events_notifiers_household_id", "households", ["household_id"], ["id"])

    with op.batch_alter_table("group_meal_plan_rules") as batch_op:
        batch_op.add_column(sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_index(op.f("ix_group_meal_plan_rules_household_id"), ["household_id"], unique=False)
        batch_op.create_foreign_key("fk_group_meal_plan_rules_household_id", "households", ["household_id"], ["id"])

    with op.batch_alter_table("invite_tokens") as batch_op:
        batch_op.add_column(sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_index(op.f("ix_invite_tokens_household_id"), ["household_id"], unique=False)
        batch_op.create_foreign_key("fk_invite_tokens_household_id", "households", ["household_id"], ["id"])

    with op.batch_alter_table("recipe_actions") as batch_op:
        batch_op.add_column(sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_index(op.f("ix_recipe_actions_household_id"), ["household_id"], unique=False)
        batch_op.create_foreign_key("fk_recipe_actions_household_id", "households", ["household_id"], ["id"])

    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_index(op.f("ix_users_household_id"), ["household_id"], unique=False)
        batch_op.create_foreign_key("fk_users_household_id", "households", ["household_id"], ["id"])

    with op.batch_alter_table("webhook_urls") as batch_op:
        batch_op.add_column(sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_index(op.f("ix_webhook_urls_household_id"), ["household_id"], unique=False)
        batch_op.create_foreign_key("fk_webhook_urls_household_id", "households", ["household_id"], ["id"])
    # ### end Alembic commands ###

    populate_household_data()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "webhook_urls", type_="foreignkey")
    op.drop_index(op.f("ix_webhook_urls_household_id"), table_name="webhook_urls")
    op.drop_column("webhook_urls", "household_id")
    op.drop_constraint(None, "users", type_="foreignkey")
    op.drop_index(op.f("ix_users_household_id"), table_name="users")
    op.drop_column("users", "household_id")
    op.drop_constraint(None, "recipe_actions", type_="foreignkey")
    op.drop_index(op.f("ix_recipe_actions_household_id"), table_name="recipe_actions")
    op.drop_column("recipe_actions", "household_id")
    op.drop_constraint(None, "invite_tokens", type_="foreignkey")
    op.drop_index(op.f("ix_invite_tokens_household_id"), table_name="invite_tokens")
    op.drop_column("invite_tokens", "household_id")
    op.drop_constraint(None, "group_meal_plan_rules", type_="foreignkey")
    op.drop_index(op.f("ix_group_meal_plan_rules_household_id"), table_name="group_meal_plan_rules")
    op.drop_column("group_meal_plan_rules", "household_id")
    op.drop_constraint(None, "group_events_notifiers", type_="foreignkey")
    op.drop_index(op.f("ix_group_events_notifiers_household_id"), table_name="group_events_notifiers")
    op.drop_column("group_events_notifiers", "household_id")
    op.drop_constraint(None, "cookbooks", type_="foreignkey")
    op.drop_index(op.f("ix_cookbooks_household_id"), table_name="cookbooks")
    op.drop_column("cookbooks", "household_id")
    op.drop_constraint("cookbook_slug_group_id_key", "cookbooks", type_="unique")
    op.drop_index(op.f("ix_household_preferences_household_id"), table_name="household_preferences")
    op.drop_index(op.f("ix_household_preferences_created_at"), table_name="household_preferences")
    op.drop_table("household_preferences")
    op.drop_index(op.f("ix_households_slug"), table_name="households")
    op.drop_index(op.f("ix_households_name"), table_name="households")
    op.drop_index(op.f("ix_households_group_id"), table_name="households")
    op.drop_index(op.f("ix_households_created_at"), table_name="households")
    op.drop_table("households")
    # ### end Alembic commands ###
