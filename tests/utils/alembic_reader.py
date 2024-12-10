import importlib.util
import pathlib
from functools import lru_cache

from mealie.db.init_db import ALEMBIC_DIR

ALEMBIC_MIGRATIONS = ALEMBIC_DIR / "versions"


def import_file(module_name: str, file_path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to import {module_name} from {file_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def latest_alembic_version() -> str:
    latest = sorted(ALEMBIC_MIGRATIONS.glob("*.py"))[-1]  # Assumes files are named in order

    mod = import_file("alembic_version", latest)

    revision = getattr(mod, "revision", None)

    if revision is None:
        raise Exception(f"Unable to find revision in {latest}")

    return revision


@lru_cache(1)
def alembic_versions():
    return [
        {"version_num": latest_alembic_version()},
    ]
