# ruff: noqa: T201
"""One-time deletion of the legacy Crowdin frontend file (issue #8721). Dry run unless CROWDIN_APPLY=true.

File 82 is the pre-Nuxt 4 path; it isn't in crowdin.yml, is never exported, and its unique
translations were already salvaged into file 100. Output is public (Actions logs).
"""

import json
import os
import urllib.request

PROJECT_ID = "451976"
BASE_URL = f"https://api.crowdin.com/api/v2/projects/{PROJECT_ID}"
HEADERS = {"Authorization": f"Bearer {os.environ['CROWDIN_API_KEY']}"}
APPLY = os.environ.get("CROWDIN_APPLY", "").lower() == "true"

FILE_ID = 82
EXPECTED_PATH = "/mealie-next/frontend/lang/messages/en-US.json"


def request(method: str, path: str) -> dict:
    req = urllib.request.Request(f"{BASE_URL}{path}", headers=HEADERS, method=method)
    with urllib.request.urlopen(req) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def main() -> None:
    print(f"MODE: {'APPLY' if APPLY else 'DRY RUN'}")
    file = request("GET", f"/files/{FILE_ID}")["data"]
    print(f"file {file['id']} path={file['path']} createdAt={file['createdAt']} updatedAt={file['updatedAt']}")
    if file["path"] != EXPECTED_PATH:
        raise RuntimeError(f"file {FILE_ID} path is {file['path']!r}, expected {EXPECTED_PATH!r}; aborting")

    if not APPLY:
        print("would delete")
        return

    request("DELETE", f"/files/{FILE_ID}")
    remaining = [f["data"]["path"] for f in request("GET", "/files?limit=500")["data"]]
    print("deleted; remaining files:")
    for path in remaining:
        print(f"  {path}")
    if EXPECTED_PATH in remaining:
        raise RuntimeError("legacy file still present after delete")


if __name__ == "__main__":
    main()
