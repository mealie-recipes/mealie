from pathlib import Path

import gen_frontend_types
import gen_locales
import gen_pytest_routes
import gen_schema_exports
import gen_test_data_paths
from _gen_utils import log

CWD = Path(__file__).parent


def main():
    items = [
        (gen_schema_exports.main, "schema exports"),
        (gen_frontend_types.main, "frontend types"),
        (gen_locales.main, "locales"),
        (gen_test_data_paths.main, "test data paths"),
        (gen_pytest_routes.main, "pytest routes"),
    ]

    for func, name in items:
        log.info(f"Generating {name}...")
        func()


if __name__ == "__main__":
    main()
