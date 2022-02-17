"""Initial tables

Revision ID: 6b0f5f32d602
Revises: 
Create Date: 2022-02-17 09:21:42.766038

"""
import sqlalchemy as sa
from sqlalchemy import engine_from_config

import mealie.db.migration_types
from alembic import op

# revision identifiers, used by Alembic.
revision = "6b0f5f32d602"
down_revision = None
branch_labels = None
depends_on = None


# Adapted from https://improveandrepeat.com/2021/09/python-friday-87-handling-pre-existing-tables-with-alembic-and-sqlalchemy/
def table_exists(table, schema=None):
    config = op.get_context().config
    engine = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.")
    insp = sa.inspect(engine)
    return insp.has_table(table, schema)


def upgrade():
    # Only create initial tables if they don't exist yet, to ease transition from pre-alembic state
    if table_exists("users"):
        return

    op.create_table(
        "events",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("text", sa.String(), nullable=True),
        sa.Column("time_stamp", sa.DateTime(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "groups",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_groups_name"), "groups", ["name"], unique=True)
    op.create_table(
        "sign_ups",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("admin", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sign_ups_name"), "sign_ups", ["name"], unique=False)
    op.create_index(op.f("ix_sign_ups_token"), "sign_ups", ["token"], unique=False)
    op.create_table(
        "categories",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", "group_id", name="category_slug_group_id_key"),
    )
    op.create_index(op.f("ix_categories_group_id"), "categories", ["group_id"], unique=False)
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=False)
    op.create_index(op.f("ix_categories_slug"), "categories", ["slug"], unique=False)
    op.create_table(
        "cookbooks",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "group_data_exports",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("size", sa.String(), nullable=False),
        sa.Column("expires", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_group_data_exports_group_id"), "group_data_exports", ["group_id"], unique=False)
    op.create_table(
        "group_events_notifiers",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("apprise_url", sa.String(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_group_events_notifiers_group_id"), "group_events_notifiers", ["group_id"], unique=False)
    op.create_table(
        "group_meal_plan_rules",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("day", sa.String(), nullable=False),
        sa.Column("entry_type", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "group_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("private_group", sa.Boolean(), nullable=True),
        sa.Column("first_day_of_week", sa.Integer(), nullable=True),
        sa.Column("recipe_public", sa.Boolean(), nullable=True),
        sa.Column("recipe_show_nutrition", sa.Boolean(), nullable=True),
        sa.Column("recipe_show_assets", sa.Boolean(), nullable=True),
        sa.Column("recipe_landscape_view", sa.Boolean(), nullable=True),
        sa.Column("recipe_disable_comments", sa.Boolean(), nullable=True),
        sa.Column("recipe_disable_amount", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_group_preferences_group_id"), "group_preferences", ["group_id"], unique=False)
    op.create_table(
        "group_reports",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_group_reports_category"), "group_reports", ["category"], unique=False)
    op.create_index(op.f("ix_group_reports_group_id"), "group_reports", ["group_id"], unique=False)
    op.create_table(
        "ingredient_units",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("abbreviation", sa.String(), nullable=True),
        sa.Column("fraction", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "invite_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("uses_left", sa.Integer(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invite_tokens_token"), "invite_tokens", ["token"], unique=True)
    op.create_table(
        "multi_purpose_labels",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("color", sa.String(length=10), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_multi_purpose_labels_group_id"), "multi_purpose_labels", ["group_id"], unique=False)
    op.create_table(
        "recipes",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("slug", sa.String(), nullable=True),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("image", sa.String(), nullable=True),
        sa.Column("total_time", sa.String(), nullable=True),
        sa.Column("prep_time", sa.String(), nullable=True),
        sa.Column("perform_time", sa.String(), nullable=True),
        sa.Column("cook_time", sa.String(), nullable=True),
        sa.Column("recipe_yield", sa.String(), nullable=True),
        sa.Column("recipeCuisine", sa.String(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("org_url", sa.String(), nullable=True),
        sa.Column("date_added", sa.Date(), nullable=True),
        sa.Column("date_updated", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], use_alter=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", "group_id", name="recipe_slug_group_id_key"),
    )
    op.create_index(op.f("ix_recipes_group_id"), "recipes", ["group_id"], unique=False)
    op.create_index(op.f("ix_recipes_slug"), "recipes", ["slug"], unique=False)
    op.create_index(op.f("ix_recipes_user_id"), "recipes", ["user_id"], unique=False)
    op.create_table(
        "server_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("completed_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("log", sa.String(), nullable=True),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_server_tasks_group_id"), "server_tasks", ["group_id"], unique=False)
    op.create_table(
        "shopping_lists",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_shopping_lists_group_id"), "shopping_lists", ["group_id"], unique=False)
    op.create_table(
        "tags",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", "group_id", name="tags_slug_group_id_key"),
    )
    op.create_index(op.f("ix_tags_group_id"), "tags", ["group_id"], unique=False)
    op.create_index(op.f("ix_tags_name"), "tags", ["name"], unique=False)
    op.create_index(op.f("ix_tags_slug"), "tags", ["slug"], unique=False)
    op.create_table(
        "tools",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("on_hand", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", "group_id", name="tools_slug_group_id_key"),
    )
    op.create_index(op.f("ix_tools_name"), "tools", ["name"], unique=True)
    op.create_index(op.f("ix_tools_slug"), "tools", ["slug"], unique=True)
    op.create_table(
        "webhook_urls",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("time", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_webhook_urls_group_id"), "webhook_urls", ["group_id"], unique=False)
    op.create_table(
        "api_extras",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipee_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("key_name", sa.String(), nullable=True),
        sa.Column("value", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipee_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cookbooks_to_categories",
        sa.Column("cookbook_id", sa.Integer(), nullable=True),
        sa.Column("category_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["cookbook_id"],
            ["cookbooks.id"],
        ),
    )
    op.create_table(
        "group2categories",
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("category_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
    )
    op.create_table(
        "group_events_notifier_options",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("event_notifier_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("recipe_created", sa.Boolean(), nullable=False),
        sa.Column("recipe_updated", sa.Boolean(), nullable=False),
        sa.Column("recipe_deleted", sa.Boolean(), nullable=False),
        sa.Column("user_signup", sa.Boolean(), nullable=False),
        sa.Column("data_migrations", sa.Boolean(), nullable=False),
        sa.Column("data_export", sa.Boolean(), nullable=False),
        sa.Column("data_import", sa.Boolean(), nullable=False),
        sa.Column("mealplan_entry_created", sa.Boolean(), nullable=False),
        sa.Column("shopping_list_created", sa.Boolean(), nullable=False),
        sa.Column("shopping_list_updated", sa.Boolean(), nullable=False),
        sa.Column("shopping_list_deleted", sa.Boolean(), nullable=False),
        sa.Column("cookbook_created", sa.Boolean(), nullable=False),
        sa.Column("cookbook_updated", sa.Boolean(), nullable=False),
        sa.Column("cookbook_deleted", sa.Boolean(), nullable=False),
        sa.Column("tag_created", sa.Boolean(), nullable=False),
        sa.Column("tag_updated", sa.Boolean(), nullable=False),
        sa.Column("tag_deleted", sa.Boolean(), nullable=False),
        sa.Column("category_created", sa.Boolean(), nullable=False),
        sa.Column("category_updated", sa.Boolean(), nullable=False),
        sa.Column("category_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_notifier_id"],
            ["group_events_notifiers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "group_meal_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("entry_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_group_meal_plans_date"), "group_meal_plans", ["date"], unique=False)
    op.create_index(op.f("ix_group_meal_plans_entry_type"), "group_meal_plans", ["entry_type"], unique=False)
    op.create_index(op.f("ix_group_meal_plans_group_id"), "group_meal_plans", ["group_id"], unique=False)
    op.create_index(op.f("ix_group_meal_plans_recipe_id"), "group_meal_plans", ["recipe_id"], unique=False)
    op.create_index(op.f("ix_group_meal_plans_title"), "group_meal_plans", ["title"], unique=False)
    op.create_table(
        "ingredient_foods",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("label_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["label_id"],
            ["multi_purpose_labels.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "notes",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("text", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "plan_rules_to_categories",
        sa.Column("group_plan_rule_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("category_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["group_plan_rule_id"],
            ["group_meal_plan_rules.id"],
        ),
    )
    op.create_table(
        "plan_rules_to_tags",
        sa.Column("plan_rule_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("tag_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["plan_rule_id"],
            ["group_meal_plan_rules.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tags.id"],
        ),
    )
    op.create_table(
        "recipe_assets",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("icon", sa.String(), nullable=True),
        sa.Column("file_name", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipe_instructions",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("text", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipe_nutrition",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("calories", sa.String(), nullable=True),
        sa.Column("fat_content", sa.String(), nullable=True),
        sa.Column("fiber_content", sa.String(), nullable=True),
        sa.Column("protein_content", sa.String(), nullable=True),
        sa.Column("carbohydrate_content", sa.String(), nullable=True),
        sa.Column("sodium_content", sa.String(), nullable=True),
        sa.Column("sugar_content", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipe_settings",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("public", sa.Boolean(), nullable=True),
        sa.Column("show_nutrition", sa.Boolean(), nullable=True),
        sa.Column("show_assets", sa.Boolean(), nullable=True),
        sa.Column("landscape_view", sa.Boolean(), nullable=True),
        sa.Column("disable_amount", sa.Boolean(), nullable=True),
        sa.Column("disable_comments", sa.Boolean(), nullable=True),
        sa.Column("locked", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipe_share_tokens",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recipe_share_tokens_group_id"), "recipe_share_tokens", ["group_id"], unique=False)
    op.create_table(
        "recipes_to_categories",
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("category_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
    )
    op.create_table(
        "recipes_to_tags",
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("tag_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tags.id"],
        ),
    )
    op.create_table(
        "recipes_to_tools",
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("tool_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tool_id"],
            ["tools.id"],
        ),
    )
    op.create_table(
        "report_entries",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=True),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column("exception", sa.String(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("report_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["group_reports.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "shopping_list_recipe_reference",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("shopping_list_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("recipe_quantity", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["shopping_list_id"],
            ["shopping_lists.id"],
        ),
        sa.PrimaryKeyConstraint("id", "shopping_list_id"),
    )
    op.create_index(
        op.f("ix_shopping_list_recipe_reference_recipe_id"),
        "shopping_list_recipe_reference",
        ["recipe_id"],
        unique=False,
    )
    op.create_table(
        "users",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("admin", sa.Boolean(), nullable=True),
        sa.Column("advanced", sa.Boolean(), nullable=True),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("cache_key", sa.String(), nullable=True),
        sa.Column("can_manage", sa.Boolean(), nullable=True),
        sa.Column("can_invite", sa.Boolean(), nullable=True),
        sa.Column("can_organize", sa.Boolean(), nullable=True),
        sa.Column("owned_recipes_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owned_recipes_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_full_name"), "users", ["full_name"], unique=False)
    op.create_index(op.f("ix_users_group_id"), "users", ["group_id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_table(
        "long_live_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_table(
        "recipe_comments",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("text", sa.String(), nullable=True),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipe_ingredient_ref_link",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("instruction_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("reference_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["instruction_id"],
            ["recipe_instructions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipes_ingredients",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column("unit_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("food_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("reference_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["food_id"],
            ["ingredient_foods.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["unit_id"],
            ["ingredient_units.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "shopping_list_items",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("shopping_list_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("is_ingredient", sa.Boolean(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("checked", sa.Boolean(), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column("is_food", sa.Boolean(), nullable=True),
        sa.Column("unit_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("food_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("label_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["food_id"],
            ["ingredient_foods.id"],
        ),
        sa.ForeignKeyConstraint(
            ["label_id"],
            ["multi_purpose_labels.id"],
        ),
        sa.ForeignKeyConstraint(
            ["shopping_list_id"],
            ["shopping_lists.id"],
        ),
        sa.ForeignKeyConstraint(
            ["unit_id"],
            ["ingredient_units.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users_to_favorites",
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
    )
    op.create_table(
        "shopping_list_item_recipe_reference",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("shopping_list_item_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("recipe_quantity", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["shopping_list_item_id"],
            ["shopping_list_items.id"],
        ),
        sa.PrimaryKeyConstraint("id", "shopping_list_item_id"),
    )
    op.create_index(
        op.f("ix_shopping_list_item_recipe_reference_recipe_id"),
        "shopping_list_item_recipe_reference",
        ["recipe_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_shopping_list_item_recipe_reference_recipe_id"), table_name="shopping_list_item_recipe_reference"
    )
    op.drop_table("shopping_list_item_recipe_reference")
    op.drop_table("users_to_favorites")
    op.drop_table("shopping_list_items")
    op.drop_table("recipes_ingredients")
    op.drop_table("recipe_ingredient_ref_link")
    op.drop_table("recipe_comments")
    op.drop_table("password_reset_tokens")
    op.drop_table("long_live_tokens")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_group_id"), table_name="users")
    op.drop_index(op.f("ix_users_full_name"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_shopping_list_recipe_reference_recipe_id"), table_name="shopping_list_recipe_reference")
    op.drop_table("shopping_list_recipe_reference")
    op.drop_table("report_entries")
    op.drop_table("recipes_to_tools")
    op.drop_table("recipes_to_tags")
    op.drop_table("recipes_to_categories")
    op.drop_index(op.f("ix_recipe_share_tokens_group_id"), table_name="recipe_share_tokens")
    op.drop_table("recipe_share_tokens")
    op.drop_table("recipe_settings")
    op.drop_table("recipe_nutrition")
    op.drop_table("recipe_instructions")
    op.drop_table("recipe_assets")
    op.drop_table("plan_rules_to_tags")
    op.drop_table("plan_rules_to_categories")
    op.drop_table("notes")
    op.drop_table("ingredient_foods")
    op.drop_index(op.f("ix_group_meal_plans_title"), table_name="group_meal_plans")
    op.drop_index(op.f("ix_group_meal_plans_recipe_id"), table_name="group_meal_plans")
    op.drop_index(op.f("ix_group_meal_plans_group_id"), table_name="group_meal_plans")
    op.drop_index(op.f("ix_group_meal_plans_entry_type"), table_name="group_meal_plans")
    op.drop_index(op.f("ix_group_meal_plans_date"), table_name="group_meal_plans")
    op.drop_table("group_meal_plans")
    op.drop_table("group_events_notifier_options")
    op.drop_table("group2categories")
    op.drop_table("cookbooks_to_categories")
    op.drop_table("api_extras")
    op.drop_index(op.f("ix_webhook_urls_group_id"), table_name="webhook_urls")
    op.drop_table("webhook_urls")
    op.drop_index(op.f("ix_tools_slug"), table_name="tools")
    op.drop_index(op.f("ix_tools_name"), table_name="tools")
    op.drop_table("tools")
    op.drop_index(op.f("ix_tags_slug"), table_name="tags")
    op.drop_index(op.f("ix_tags_name"), table_name="tags")
    op.drop_index(op.f("ix_tags_group_id"), table_name="tags")
    op.drop_table("tags")
    op.drop_index(op.f("ix_shopping_lists_group_id"), table_name="shopping_lists")
    op.drop_table("shopping_lists")
    op.drop_index(op.f("ix_server_tasks_group_id"), table_name="server_tasks")
    op.drop_table("server_tasks")
    op.drop_index(op.f("ix_recipes_user_id"), table_name="recipes")
    op.drop_index(op.f("ix_recipes_slug"), table_name="recipes")
    op.drop_index(op.f("ix_recipes_group_id"), table_name="recipes")
    op.drop_table("recipes")
    op.drop_index(op.f("ix_multi_purpose_labels_group_id"), table_name="multi_purpose_labels")
    op.drop_table("multi_purpose_labels")
    op.drop_index(op.f("ix_invite_tokens_token"), table_name="invite_tokens")
    op.drop_table("invite_tokens")
    op.drop_table("ingredient_units")
    op.drop_index(op.f("ix_group_reports_group_id"), table_name="group_reports")
    op.drop_index(op.f("ix_group_reports_category"), table_name="group_reports")
    op.drop_table("group_reports")
    op.drop_index(op.f("ix_group_preferences_group_id"), table_name="group_preferences")
    op.drop_table("group_preferences")
    op.drop_table("group_meal_plan_rules")
    op.drop_index(op.f("ix_group_events_notifiers_group_id"), table_name="group_events_notifiers")
    op.drop_table("group_events_notifiers")
    op.drop_index(op.f("ix_group_data_exports_group_id"), table_name="group_data_exports")
    op.drop_table("group_data_exports")
    op.drop_table("cookbooks")
    op.drop_index(op.f("ix_categories_slug"), table_name="categories")
    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.drop_index(op.f("ix_categories_group_id"), table_name="categories")
    op.drop_table("categories")
    op.drop_index(op.f("ix_sign_ups_token"), table_name="sign_ups")
    op.drop_index(op.f("ix_sign_ups_name"), table_name="sign_ups")
    op.drop_table("sign_ups")
    op.drop_index(op.f("ix_groups_name"), table_name="groups")
    op.drop_table("groups")
    op.drop_table("events")
