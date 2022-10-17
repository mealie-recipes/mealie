from pathlib import Path

import gen_frontend_types
import gen_locales
import gen_pytest_routes
import gen_schema_exports
import gen_test_data_paths

CWD = Path(__file__).parent


def main():
    gen_locales.main()
    gen_test_data_paths.main()
    gen_schema_exports.main()
    gen_pytest_routes.main()
    gen_frontend_types.main()


if __name__ == "__main__":
    main()
