"""Workflow 5 merge check: JSON key style and id format across every GET path in parity.hurl.

For each GET the candidate is asked, fetch Python :9000 and PHP :9001 with the same token and report:
- keys present on one side only (recursive key paths, list indexes collapsed), and whether they look snake_case;
- id-like strings that are 32-char hex (undashed) on the PHP side.
Token is read from the file given as argv[1] and never printed.
"""

# ruff: noqa: T201

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEX32 = re.compile(r"^[0-9a-f]{32}$")


def fetch(base: str, path: str, token: str) -> tuple[int, object]:
    req = urllib.request.Request(base + path, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            status, body = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, body = e.code, e.read()
    try:
        return status, json.loads(body)
    except ValueError:
        return status, None


def keys(value: object, prefix: str = "$") -> set[str]:
    out: set[str] = set()
    if isinstance(value, dict):
        for k, v in value.items():
            out.add(f"{prefix}.{k}")
            out |= keys(v, f"{prefix}.{k}")
    elif isinstance(value, list):
        for item in value:
            out |= keys(item, f"{prefix}[]")
    return out


def hex_ids(value: object, prefix: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for k, v in value.items():
            found += hex_ids(v, f"{prefix}.{k}")
    elif isinstance(value, list):
        for item in value:
            found += hex_ids(item, f"{prefix}[]")
    elif isinstance(value, str) and HEX32.match(value):
        found.append(prefix)
    return found


def main() -> None:
    token = Path(sys.argv[1]).read_text().strip()
    lines = (ROOT / "compx574/hurl/parity.hurl").read_text().splitlines()
    paths = sorted({ln.split("}}", 1)[1] for ln in lines if ln.startswith("GET {{candidate}}")})
    both_200 = key_diff = hex_hits = 0
    for path in paths:
        ps, pb = fetch("http://127.0.0.1:9000", path, token)
        hs, hb = fetch("http://127.0.0.1:9001", path, token)
        if ps != 200 or hs != 200:
            continue
        both_200 += 1
        only_py = sorted(keys(pb) - keys(hb))
        only_php = sorted(keys(hb) - keys(pb))
        hexes = sorted(set(hex_ids(hb)) - set(hex_ids(pb)))
        if only_py or only_php or hexes:
            print(f"{path}")
            for k in only_py[:8]:
                print(f"  only python: {k}")
            for k in only_php[:8]:
                snake = " (snake_case)" if "_" in k.rsplit(".", 1)[-1] else ""
                print(f"  only php:    {k}{snake}")
            for k in hexes[:8]:
                print(f"  undashed id on php: {k}")
        key_diff += bool(only_py or only_php)
        hex_hits += bool(hexes)
    print(f"GET paths={len(paths)} both_200={both_200} key_set_differs={key_diff} php_undashed_ids={hex_hits}")


if __name__ == "__main__":
    main()
