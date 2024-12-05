"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types
% if imports:
${imports}
% endif

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision: str | None = ${repr(down_revision)}
branch_labels: str | tuple[str, ...] | None = ${repr(branch_labels)}
depends_on: str | tuple[str, ...] | None = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
