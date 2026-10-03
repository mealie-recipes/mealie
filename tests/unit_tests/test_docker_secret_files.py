"""Secret loading regressions, runnable without application dependencies."""

import os
import tempfile
import unittest
from pathlib import Path

from tests.docker_entrypoint import run_entrypoint

ENTRYPOINT = Path(__file__).resolve().parents[2] / "docker" / "entry.sh"


class DockerSecretFilesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory(prefix="mealie-secret-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def assert_rejected(self, path: Path, commands: dict[str, str] | None = None) -> None:
        result = run_entrypoint(
            ENTRYPOINT,
            {"POSTGRES_PASSWORD_FILE": str(path), "POSTGRES_PASSWORD": "base-secret-must-not-leak"},
            commands,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("APP_STARTED", result.stdout)
        self.assertIn("POSTGRES_PASSWORD_FILE", result.stderr)
        self.assertNotIn("base-secret-must-not-leak", result.stdout + result.stderr)
        self.assertNotIn("file-secret-must-not-leak", result.stdout + result.stderr)

    def test_missing_file_stops_startup_even_with_base_value(self) -> None:
        self.assert_rejected(self.root / "missing")

    def test_directory_is_rejected(self) -> None:
        self.assert_rejected(self.root)

    def test_empty_and_newline_only_files_are_rejected(self) -> None:
        path = self.root / "secret"
        for contents in ("", "\n", "\n\n"):
            with self.subTest(contents=contents):
                path.write_text(contents)
                self.assert_rejected(path)

    @unittest.skipIf(os.geteuid() == 0, "Root can read files despite their permission bits")
    def test_unreadable_file_is_rejected(self) -> None:
        path = self.root / "secret"
        path.write_text("file-secret-must-not-leak")
        path.chmod(0o000)
        try:
            self.assert_rejected(path)
        finally:
            path.chmod(0o600)

    def test_read_failure_after_validation_stops_startup(self) -> None:
        path = self.root / "secret"
        path.write_text("file-secret-must-not-leak")
        self.assert_rejected(path, {"cat": "echo file-secret-must-not-leak >&2\nexit 1\n"})

    def test_file_overrides_base_value_without_interpreting_its_contents(self) -> None:
        path = self.root / "secret with spaces"
        value = "literal-$value-$(false)-'quoted'\\value\nsecond line"
        path.write_text(value + "\n\n")
        result = run_entrypoint(ENTRYPOINT, {"POSTGRES_PASSWORD_FILE": str(path), "POSTGRES_PASSWORD": "base-value"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"POSTGRES_PASSWORD={value}\n", result.stdout)

    def test_secret_volume_symlinks_are_supported(self) -> None:
        target = self.root / "target"
        target.write_text("linked-secret\n")
        path = self.root / "secret"
        path.symlink_to(target)
        result = run_entrypoint(ENTRYPOINT, {"SMTP_PASSWORD_FILE": str(path)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SMTP_PASSWORD=linked-secret\n", result.stdout)

    def test_unconfigured_file_preserves_base_value(self) -> None:
        for environment in ({"SMTP_PASSWORD": "base-value"}, {"SMTP_PASSWORD_FILE": "", "SMTP_PASSWORD": "base-value"}):
            with self.subTest(environment=environment):
                result = run_entrypoint(ENTRYPOINT, environment)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("SMTP_PASSWORD=base-value\n", result.stdout)


if __name__ == "__main__":
    unittest.main()
