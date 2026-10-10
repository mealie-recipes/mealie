"""Entrypoint regressions, runnable without installing the application dependencies."""

import unittest
from pathlib import Path

from tests.docker_entrypoint import run_entrypoint

ENTRYPOINT = Path(__file__).resolve().parents[2] / "docker" / "entry.sh"


class DockerProxyTrustTests(unittest.TestCase):
    def test_explicit_proxy_allowlist_survives_startup(self) -> None:
        for value in ("10.42.1.0/24", "127.0.0.1,::1,10.42.1.0/24", "*", ""):
            with self.subTest(value=value):
                result = run_entrypoint(ENTRYPOINT, {"HOST_IP": value})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("APP_STARTED", result.stdout)
                self.assertIn(f"HOST_IP={value}\n", result.stdout)

    def test_unset_proxy_setting_is_left_to_application_default(self) -> None:
        result = run_entrypoint(ENTRYPOINT, {})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("HOST_IP=UNSET\n", result.stdout)


if __name__ == "__main__":
    unittest.main()
