import argparse
from pathlib import Path

import gen_py_pytest_data_paths
import gen_py_pytest_routes
import gen_py_schema_exports
import gen_ts_locales
import gen_ts_types
import gen_ts_unit_systems
from utils import log

CWD = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(description="Run code generators")
    parser.add_argument(
        "generators",
        nargs="*",
        help="Specific generators to run (schema, types, locales, unit-systems, data-paths, routes, crowdin-approvals). If none specified, all except crowdin-approvals will run.",  # noqa: E501 - long line
    )
    args = parser.parse_args()

    # Define all available generators
    all_generators = {
        "schema": (gen_py_schema_exports.main, "schema exports"),
        "types": (gen_ts_types.main, "frontend types"),
        "locales": (gen_ts_locales.main, "locales"),
        "unit-systems": (gen_ts_unit_systems.main, "unit systems"),
        "data-paths": (gen_py_pytest_data_paths.main, "test data paths"),
        "routes": (gen_py_pytest_routes.main, "pytest routes"),
        "crowdin-approvals": (gen_ts_locales.remove_crowdin_approvals, "Crowdin approval removal"),
    }

    # Changes Crowdin rather than local files, so it only runs when requested
    opt_in_generators = {"crowdin-approvals"}

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
        generators_to_run = [value for key, value in all_generators.items() if key not in opt_in_generators]

    # Run the selected generators
    for func, name in generators_to_run:
        log.info(f"Generating {name}...")
        func()


if __name__ == "__main__":
    main()
