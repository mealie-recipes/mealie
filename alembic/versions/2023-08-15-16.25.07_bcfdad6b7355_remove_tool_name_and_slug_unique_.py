"""remove tool name and slug unique contraints

Revision ID: bcfdad6b7355
Revises: 1825b5225403
Create Date: 2023-08-15 16:25:07.058929

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "bcfdad6b7355"
down_revision = "1825b5225403"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_tools_name", table_name="tools")
    op.create_index(op.f("ix_tools_name"), "tools", ["name"], unique=False)
    op.drop_index("ix_tools_slug", table_name="tools")
    op.create_index(op.f("ix_tools_slug"), "tools", ["slug"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_tools_slug"), table_name="tools")
    op.create_index("ix_tools_slug", "tools", ["slug"], unique=True)
    op.drop_index(op.f("ix_tools_name"), table_name="tools")
    op.create_index("ix_tools_name", "tools", ["name"], unique=True)
    # ### end Alembic commands ###
