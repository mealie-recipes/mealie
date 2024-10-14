"""add auth_method to user table

Revision ID: 38514b39a824
Revises: b04a08da2108
Create Date: 2023-02-22 21:45:52.900964

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "38514b39a824"
down_revision = "b04a08da2108"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


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
