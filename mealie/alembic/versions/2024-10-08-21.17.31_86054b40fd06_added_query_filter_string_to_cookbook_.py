"""added query_filter_string to cookbook and mealplan

Revision ID: 86054b40fd06
Revises: 602927e1013e
Create Date: 2024-10-08 21:17:31.601903

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm

from mealie.db.models._model_utils import guid

# revision identifiers, used by Alembic.
revision = "86054b40fd06"
down_revision: str | None = "602927e1013e"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


# Intermediate table definitions
class SqlAlchemyBase(orm.DeclarativeBase):
    pass


class Category(SqlAlchemyBase):
    __tablename__ = "categories"
    id: orm.Mapped[guid.GUID] = orm.mapped_column(guid.GUID, primary_key=True, default=guid.GUID.generate)


class Tag(SqlAlchemyBase):
    __tablename__ = "tags"
    id: orm.Mapped[guid.GUID] = orm.mapped_column(guid.GUID, primary_key=True, default=guid.GUID.generate)


class Tool(SqlAlchemyBase):
    __tablename__ = "tools"
    id: orm.Mapped[guid.GUID] = orm.mapped_column(guid.GUID, primary_key=True, default=guid.GUID.generate)


class Household(SqlAlchemyBase):
    __tablename__ = "households"
    id: orm.Mapped[guid.GUID] = orm.mapped_column(guid.GUID, primary_key=True, default=guid.GUID.generate)


cookbooks_to_categories = sa.Table(
    "cookbooks_to_categories",
    SqlAlchemyBase.metadata,
    sa.Column("cookbook_id", guid.GUID, sa.ForeignKey("cookbooks.id"), index=True),
    sa.Column("category_id", guid.GUID, sa.ForeignKey("categories.id"), index=True),
)

cookbooks_to_tags = sa.Table(
    "cookbooks_to_tags",
    SqlAlchemyBase.metadata,
    sa.Column("cookbook_id", guid.GUID, sa.ForeignKey("cookbooks.id"), index=True),
    sa.Column("tag_id", guid.GUID, sa.ForeignKey("tags.id"), index=True),
)

cookbooks_to_tools = sa.Table(
    "cookbooks_to_tools",
    SqlAlchemyBase.metadata,
    sa.Column("cookbook_id", guid.GUID, sa.ForeignKey("cookbooks.id"), index=True),
    sa.Column("tool_id", guid.GUID, sa.ForeignKey("tools.id"), index=True),
)

plan_rules_to_categories = sa.Table(
    "plan_rules_to_categories",
    SqlAlchemyBase.metadata,
    sa.Column("group_plan_rule_id", guid.GUID, sa.ForeignKey("group_meal_plan_rules.id"), index=True),
    sa.Column("category_id", guid.GUID, sa.ForeignKey("categories.id"), index=True),
)

plan_rules_to_tags = sa.Table(
    "plan_rules_to_tags",
    SqlAlchemyBase.metadata,
    sa.Column("plan_rule_id", guid.GUID, sa.ForeignKey("group_meal_plan_rules.id"), index=True),
    sa.Column("tag_id", guid.GUID, sa.ForeignKey("tags.id"), index=True),
)

plan_rules_to_households = sa.Table(
    "plan_rules_to_households",
    SqlAlchemyBase.metadata,
    sa.Column("group_plan_rule_id", guid.GUID, sa.ForeignKey("group_meal_plan_rules.id"), index=True),
    sa.Column("household_id", guid.GUID, sa.ForeignKey("households.id"), index=True),
)


class CookBook(SqlAlchemyBase):
    __tablename__ = "cookbooks"

    id: orm.Mapped[guid.GUID] = orm.mapped_column(guid.GUID, primary_key=True, default=guid.GUID.generate)
    query_filter_string: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False, default="")

    categories: orm.Mapped[list[Category]] = orm.relationship(
        Category, secondary=cookbooks_to_categories, single_parent=True
    )
    require_all_categories: orm.Mapped[bool | None] = orm.mapped_column(sa.Boolean, default=True)

    tags: orm.Mapped[list[Tag]] = orm.relationship(Tag, secondary=cookbooks_to_tags, single_parent=True)
    require_all_tags: orm.Mapped[bool | None] = orm.mapped_column(sa.Boolean, default=True)

    tools: orm.Mapped[list[Tool]] = orm.relationship(Tool, secondary=cookbooks_to_tools, single_parent=True)
    require_all_tools: orm.Mapped[bool | None] = orm.mapped_column(sa.Boolean, default=True)


class GroupMealPlanRules(SqlAlchemyBase):
    __tablename__ = "group_meal_plan_rules"

    id: orm.Mapped[guid.GUID] = orm.mapped_column(guid.GUID, primary_key=True, default=guid.GUID.generate)
    query_filter_string: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False, default="")

    categories: orm.Mapped[list[Category]] = orm.relationship(Category, secondary=plan_rules_to_categories)
    tags: orm.Mapped[list[Tag]] = orm.relationship(Tag, secondary=plan_rules_to_tags)
    households: orm.Mapped[list["Household"]] = orm.relationship("Household", secondary=plan_rules_to_households)


def migrate_cookbooks():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    cookbooks = session.query(CookBook).all()
    for cookbook in cookbooks:
        parts = []
        if cookbook.categories:
            relop = "CONTAINS ALL" if cookbook.require_all_categories else "IN"
            vals = ",".join([f'"{cat.id}"' for cat in cookbook.categories])
            parts.append(f"recipe_category.id {relop} [{vals}]")
        if cookbook.tags:
            relop = "CONTAINS ALL" if cookbook.require_all_tags else "IN"
            vals = ",".join([f'"{tag.id}"' for tag in cookbook.tags])
            parts.append(f"tags.id {relop} [{vals}]")
        if cookbook.tools:
            relop = "CONTAINS ALL" if cookbook.require_all_tools else "IN"
            vals = ",".join([f'"{tool.id}"' for tool in cookbook.tools])
            parts.append(f"tools.id {relop} [{vals}]")

        cookbook.query_filter_string = " AND ".join(parts)

    session.commit()


def migrate_mealplan_rules():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    rules = session.query(GroupMealPlanRules).all()
    for rule in rules:
        parts = []
        if rule.categories:
            vals = ",".join([f'"{cat.id}"' for cat in rule.categories])
            parts.append(f"recipe_category.id CONTAINS ALL [{vals}]")
        if rule.tags:
            vals = ",".join([f'"{tag.id}"' for tag in rule.tags])
            parts.append(f"tags.id CONTAINS ALL [{vals}]")
        if rule.households:
            vals = ",".join([f'"{household.id}"' for household in rule.households])
            parts.append(f"household_id IN [{vals}]")

        rule.query_filter_string = " AND ".join(parts)

    session.commit()


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("cookbooks", schema=None) as batch_op:
        batch_op.add_column(sa.Column("query_filter_string", sa.String(), nullable=False, server_default=""))

    with op.batch_alter_table("group_meal_plan_rules", schema=None) as batch_op:
        batch_op.add_column(sa.Column("query_filter_string", sa.String(), nullable=False, server_default=""))

    # ### end Alembic commands ###

    migrate_cookbooks()
    migrate_mealplan_rules()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("group_meal_plan_rules", schema=None) as batch_op:
        batch_op.drop_column("query_filter_string")

    with op.batch_alter_table("cookbooks", schema=None) as batch_op:
        batch_op.drop_column("query_filter_string")

    # ### end Alembic commands ###
