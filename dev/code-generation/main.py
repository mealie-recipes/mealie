from pathlib import Path

import gen_py_pytest_data_paths
import gen_py_pytest_routes
import gen_py_schema_exports
import gen_ts_locales
import gen_ts_types
from utils import log

CWD = Path(__file__).parent


def main():
    items = [
        (gen_py_schema_exports.main, "schema exports"),
        (gen_ts_types.main, "frontend types"),
        (gen_ts_locales.main, "locales"),
        (gen_py_pytest_data_paths.main, "test data paths"),
        (gen_py_pytest_routes.main, "pytest routes"),
    ]

    for func, name in items:
        log.info(f"Generating {name}...")
        func()


if __name__ == "__main__":
    main()
