"""adds auth_method to user table

Revision ID: 59da1a87a3b7
Revises: 16160bf731a0
Create Date: 2023-02-16 21:26:00.693018

"""
import sqlalchemy as sa

import mealie.db.migration_types
from alembic import op

# revision identifiers, used by Alembic.
revision = "59da1a87a3b7"
down_revision = "16160bf731a0"
branch_labels = None
depends_on = None


def is_postgres():
    return op.get_context().dialect.name == "postgresql"


authMethod = sa.Enum("MEALIE", "LDAP", name="authmethod")


def upgrade():
    if is_postgres():
        authMethod.create(op.get_bind())

    op.add_column(
        "users",
        sa.Column("auth_method", authMethod, nullable=False, server_default="MEALIE"),
    )
    op.execute("UPDATE users SET auth_method = 'LDAP' WHERE password = 'LDAP'")


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("auth_method")

    if is_postgres():
        authMethod.drop(op.get_bind())
