import argparse
from pathlib import Path

import gen_py_pytest_data_paths
import gen_py_pytest_routes
import gen_py_schema_exports
import gen_ts_locales
import gen_ts_types
from utils import log

CWD = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(description="Run code generators")
    parser.add_argument(
        "generators",
        nargs="*",
        help="Specific generators to run (schema, types, locales, data-paths, routes). If none specified, all will run.",  # noqa: E501 - long line
    )
    args = parser.parse_args()

    # Define all available generators
    all_generators = {
        "schema": (gen_py_schema_exports.main, "schema exports"),
        "types": (gen_ts_types.main, "frontend types"),
        "locales": (gen_ts_locales.main, "locales"),
        "data-paths": (gen_py_pytest_data_paths.main, "test data paths"),
        "routes": (gen_py_pytest_routes.main, "pytest routes"),
    }

    # Determine which generators to run
    if args.generators:
        # Validate requested generators
        invalid_generators = [g for g in args.generators if g not in all_generators]
        if invalid_generators:
            log.error(f"Invalid generator(s): {', '.join(invalid_generators)}")
            log.info(f"Available generators: {', '.join(all_generators.keys())}")
            return

        generators_to_run = [(all_generators[g][0], all_generators[g][1]) for g in args.generators]
    else:
        # Run all generators (default behavior)
        generators_to_run = list(all_generators.values())

    # Run the selected generators
    for func, name in generators_to_run:
        log.info(f"Generating {name}...")
        func()


if __name__ == "__main__":
    main()
