import sqlite3
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
import sqlalchemy.exc

from mealie.routes._base.mixins import is_unique_violation


def make_postgres_integrity_error(pgcode: str) -> sqlalchemy.exc.IntegrityError:
    psycopg2 = pytest.importorskip("psycopg2", reason="psycopg2 is only installed with the pgsql extra")

    orig = Mock(spec=psycopg2.Error)
    orig.pgcode = pgcode
    return sqlalchemy.exc.IntegrityError(None, None, orig)


@patch("mealie.routes._base.mixins.get_app_settings")
@pytest.mark.parametrize(
    ("pgcode", "expected"),
    [
        ("23505", True),  # unique_violation
        ("23503", False),  # foreign_key_violation
    ],
)
def test_is_unique_violation_postgres(mock_settings, pgcode, expected):
    mock_settings.return_value = SimpleNamespace(DB_ENGINE="postgres")

    ex = make_postgres_integrity_error(pgcode)

    assert is_unique_violation(ex) is expected


def make_sqlite_integrity_error(sqlite_errorcode: int) -> sqlalchemy.exc.IntegrityError:
    orig = sqlite3.IntegrityError()
    orig.sqlite_errorcode = sqlite_errorcode
    return sqlalchemy.exc.IntegrityError(None, None, orig)


@patch("mealie.routes._base.mixins.get_app_settings")
@pytest.mark.parametrize(
    ("sqlite_errorcode", "expected"),
    [
        (sqlite3.SQLITE_CONSTRAINT_UNIQUE, True),
        (sqlite3.SQLITE_CONSTRAINT_PRIMARYKEY, False),
    ],
)
def test_is_unique_violation_sqlite(mock_settings, sqlite_errorcode, expected):
    mock_settings.return_value = SimpleNamespace(DB_ENGINE="sqlite")

    ex = make_sqlite_integrity_error(sqlite_errorcode)

    assert is_unique_violation(ex) is expected
