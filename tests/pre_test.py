from mealie.core.config import determine_sqlite_path, settings

DB_URL = determine_sqlite_path(path=True, suffix="test")
DB_URL.unlink(missing_ok=True)

if settings.DB_ENGINE != "postgres":
    # Monkeypatch Database Testing
    settings.DB_URL = determine_sqlite_path(path=False, suffix="test")
