from mealie.core.config import app_dirs, settings

# Monkeypatch Database Testing
DB_URL = app_dirs.DATA_DIR.joinpath("test.db")
DB_URL.unlink(missing_ok=True)

settings.DB_URL = "sqlite:///" + str(DB_URL.absolute())
