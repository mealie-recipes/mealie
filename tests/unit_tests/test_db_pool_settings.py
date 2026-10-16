import os
from contextlib import ExitStack
from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import TimeoutError as PoolTimeoutError
from sqlalchemy.pool import QueuePool, SingletonThreadPool

from mealie.core.config import get_app_settings
from mealie.core.settings.db_providers import PostgresProvider
from mealie.db import db_setup


@pytest.fixture
def postgres_settings(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DB_ENGINE", "postgres")
    for name in ("POSTGRES_POOL_SIZE", "POSTGRES_MAX_OVERFLOW", "POSTGRES_POOL_TIMEOUT"):
        monkeypatch.delenv(name, raising=False)
    get_app_settings.cache_clear()
    yield
    get_app_settings.cache_clear()


@pytest.mark.usefixtures("postgres_settings")
@pytest.mark.parametrize("override_url", [False, True])
def test_postgres_pool_uses_environment_settings(monkeypatch: pytest.MonkeyPatch, override_url: bool):
    pytest.importorskip("psycopg2")
    monkeypatch.setenv("POSTGRES_POOL_SIZE", "12")
    monkeypatch.setenv("POSTGRES_MAX_OVERFLOW", "0")
    monkeypatch.setenv("POSTGRES_POOL_TIMEOUT", "0.25")
    if override_url:
        monkeypatch.setenv("POSTGRES_URL_OVERRIDE", "postgresql://mealie:mealie@localhost/mealie")
    else:
        monkeypatch.delenv("POSTGRES_URL_OVERRIDE", raising=False)
    settings = get_app_settings()
    monkeypatch.setattr(db_setup, "settings", settings)

    _, engine = db_setup.sql_global_init(settings.DB_URL)
    try:
        assert isinstance(engine.pool, QueuePool)
        assert engine.pool.size() == 12
        assert engine.pool.timeout() == 0.25
        assert engine.pool._max_overflow == 0
    finally:
        engine.dispose()


@pytest.mark.usefixtures("postgres_settings")
def test_postgres_pool_preserves_defaults(monkeypatch: pytest.MonkeyPatch):
    pytest.importorskip("psycopg2")
    settings = get_app_settings()
    monkeypatch.setattr(db_setup, "settings", settings)
    _, engine = db_setup.sql_global_init(settings.DB_URL)
    try:
        assert isinstance(engine.pool, QueuePool)
        assert engine.pool.size() == 5
        assert engine.pool.timeout() == 30
        assert engine.pool._max_overflow == 10
    finally:
        engine.dispose()


@pytest.mark.usefixtures("postgres_settings")
@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("POSTGRES_POOL_SIZE", "0"),
        ("POSTGRES_POOL_SIZE", "-1"),
        ("POSTGRES_MAX_OVERFLOW", "-1"),
        ("POSTGRES_POOL_TIMEOUT", "-0.1"),
        ("POSTGRES_POOL_TIMEOUT", "nan"),
        ("POSTGRES_POOL_TIMEOUT", "inf"),
    ],
)
def test_postgres_pool_rejects_invalid_settings(monkeypatch: pytest.MonkeyPatch, name: str, value: str):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValidationError, match=name):
        get_app_settings()


@pytest.mark.usefixtures("postgres_settings")
def test_postgres_pool_allows_no_wait(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRES_POOL_TIMEOUT", "0")
    provider = get_app_settings().DB_PROVIDER
    assert isinstance(provider, PostgresProvider)
    assert provider.POSTGRES_POOL_TIMEOUT == 0


def test_postgres_pool_capacity_and_recovery(monkeypatch: pytest.MonkeyPatch):
    if os.environ.get("DB_ENGINE") != "postgres":
        pytest.skip("Requires the PostgreSQL test database")
    monkeypatch.setenv("POSTGRES_POOL_SIZE", "1")
    monkeypatch.setenv("POSTGRES_MAX_OVERFLOW", "1")
    monkeypatch.setenv("POSTGRES_POOL_TIMEOUT", "0.01")
    get_app_settings.cache_clear()
    try:
        settings = get_app_settings()
        monkeypatch.setattr(db_setup, "settings", settings)
        _, engine = db_setup.sql_global_init(settings.DB_URL)
        try:
            with ExitStack() as stack:
                first = stack.enter_context(engine.connect())
                stack.enter_context(engine.connect())
                with pytest.raises(PoolTimeoutError):
                    with engine.connect():
                        pytest.fail("Pool allowed more connections than configured")
                first.close()
                with engine.connect() as connection:
                    assert connection.exec_driver_sql("SELECT 1").scalar_one() == 1
        finally:
            engine.dispose()
    finally:
        get_app_settings.cache_clear()


@pytest.mark.parametrize("in_memory", [False, True])
def test_sqlite_ignores_postgres_pool_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, in_memory: bool):
    monkeypatch.setenv("DB_ENGINE", "sqlite")
    monkeypatch.setenv("POSTGRES_POOL_SIZE", "0")
    get_app_settings.cache_clear()
    try:
        monkeypatch.setattr(db_setup, "settings", get_app_settings())
        url = "sqlite:///:memory:" if in_memory else f"sqlite:///{tmp_path / 'pool.db'}"
        _, engine = db_setup.sql_global_init(url)
        try:
            if in_memory:
                assert isinstance(engine.pool, SingletonThreadPool)
            else:
                assert isinstance(engine.pool, QueuePool)
                assert engine.pool.size() == 5
                assert engine.pool.timeout() == 30
            with engine.connect() as connection:
                assert connection.exec_driver_sql("SELECT 1").scalar_one() == 1
        finally:
            engine.dispose()
    finally:
        get_app_settings.cache_clear()
