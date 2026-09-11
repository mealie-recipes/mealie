"""redact passwords from user login history reasons

Revision ID: a1b2c3d4e5f6
Revises: 2c84028bd4ce
Create Date: 2026-09-11 12:00:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision: str | None = "2c84028bd4ce"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    # Older /login failures stored plaintext credentials in reason (e.g. "invalid_credentials. user / pass").
    op.execute(
        """
        UPDATE user_login_history
        SET reason = 'invalid_credentials'
        WHERE reason LIKE 'invalid_credentials.%'
        """
    )


def downgrade():
    pass
