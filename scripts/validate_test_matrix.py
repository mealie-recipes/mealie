#!/usr/bin/env python3
"""
Validate that all test directories are covered by the GitHub Actions test matrix.
"""

import re
import sys
from pathlib import Path
from typing import Literal

WORKFLOW_FILEPATH = Path(".github/workflows/test-backend.yml")


def get_test_directories() -> list[str]:
    """Get all directories containing test files."""
    tests_dir = Path("tests")
    if not tests_dir.exists():
        return []

    directories = set()
    for test_file in tests_dir.rglob("test_*.py"):
        rel_path = test_file.relative_to(tests_dir)
        if rel_path.parent != Path("."):
            directories.add(str(rel_path.parent))

    return sorted(directories)


def get_matrix_suites_from_workflow() -> list[str]:
    """Parse the GitHub Actions workflow file to extract the TestSuite matrix."""
    if not WORKFLOW_FILEPATH.exists():
        sys.stderr.write(f"❌ Workflow file not found: {WORKFLOW_FILEPATH}\n")
        return []

    content = WORKFLOW_FILEPATH.read_text()

    # Look for the pattern: TestSuite: [ ... ]
    pattern = r"TestSuite:\s*\[(.*?)\]"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        sys.stderr.write("❌ Could not find TestSuite matrix in workflow file\n")
        return []

    matrix_content: str = match.group(1)
    test_suites = []
    for line in matrix_content.split(","):
        suite = line.strip().split("#")[0].strip()  # Remove comments
        suite = suite.strip("\"'")  # Remove quotes
        if not suite:
            continue

        test_suites.append(suite)

    return test_suites


def main() -> Literal[0, 1]:
    """Validate test coverage."""
    test_dirs = get_test_directories()
    matrix_suites = get_matrix_suites_from_workflow()

    if not matrix_suites:
        sys.stderr.write("❌ Could not extract TestSuite matrix from workflow file\n")
        return 1

    missing_dirs = []
    for test_dir in test_dirs:
        covered = any(test_dir.startswith(suite) or suite.startswith(test_dir) for suite in matrix_suites)

        if not covered:
            missing_dirs.append(test_dir)

    if missing_dirs:
        sys.stderr.write("❌ Test directories not covered by GitHub Actions matrix:\n")
        for missing_dir in missing_dirs:
            sys.stderr.write(f"   • {missing_dir}\n")
        sys.stderr.write("\nPlease add these to the TestSuite matrix in .github/workflows/test-backend.yml\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
