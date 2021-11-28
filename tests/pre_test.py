import os

from mealie.core.config import get_app_dirs, get_app_settings
from mealie.core.settings.db_providers import SQLiteProvider

os.environ["PRODUCTION"] = "True"
os.environ["TESTING"] = "True"

settings = get_app_settings()
app_dirs = get_app_dirs()
settings.DB_PROVIDER = SQLiteProvider(data_dir=app_dirs.DATA_DIR, prefix="test_")

if settings.DB_ENGINE != "postgres":
    # Monkeypatch Database Testing
    settings.DB_PROVIDER = SQLiteProvider(data_dir=app_dirs.DATA_DIR, prefix="test_")
