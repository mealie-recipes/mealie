"""Workflow 5 merge check: status codes for every GET path in parity.hurl as a non-admin user and with no token.

Usage: perm_compare.py <token-file|-> <label>. "-" means no Authorization header. Token is never printed.
"""

# ruff: noqa: T201

import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def status(base: str, path: str, token: str | None) -> int:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        with urllib.request.urlopen(urllib.request.Request(base + path, headers=headers), timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def main() -> None:
    token = None if sys.argv[1] == "-" else Path(sys.argv[1]).read_text().strip()
    lines = (ROOT / "compx574/hurl/parity.hurl").read_text().splitlines()
    paths = sorted({ln.split("}}", 1)[1] for ln in lines if ln.startswith("GET {{candidate}}")})
    same = differ = 0
    for path in paths:
        py, php = status("http://127.0.0.1:9000", path, token), status("http://127.0.0.1:9001", path, token)
        if php == 404 and py != 404:
            continue  # route not registered in PHP; counted by measure.sh
        if py == php:
            same += 1
        else:
            differ += 1
            print(f"DIFF {sys.argv[2]} {path} python={py} php={php}")
    print(f"{sys.argv[2]}: registered GET paths compared={same + differ} same_status={same} differ={differ}")


if __name__ == "__main__":
    main()
