"""Compare PHP and Python responses for the same Mealie database.

Reads are GET-only. The token is minted with Mealie's own signer and is not printed.
"""

# ruff: noqa: T201

from __future__ import annotations

import json
import re
import sqlite3
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "dev" / "data" / "mealie.db"
PY = "http://127.0.0.1:9000"
PHP = "http://127.0.0.1:9001"


def dashed(hex_id: str) -> str:
    hex_id = hex_id.replace("-", "")
    return f"{hex_id[0:8]}-{hex_id[8:12]}-{hex_id[12:16]}-{hex_id[16:20]}-{hex_id[20:32]}"


def token_for_first_user() -> str:
    row = sqlite3.connect(DB).execute("select id from users order by username limit 1").fetchone()
    subject = dashed(row[0])
    script = f"""
require 'vendor/autoload.php';
$app = require 'bootstrap/app.php';
$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();
echo App\\Auth\\Jwt::encode([
    'sub' => '{subject}',
    'rme' => false,
    'iss' => 'mealie',
    'iat' => time(),
    'exp' => time() + 3600,
], App\\Auth\\Jwt::secret());
"""
    result = subprocess.run(
        ["php", "-r", script],
        cwd=ROOT / "php-w1",
        check=True,
        capture_output=True,
        text=True,
    )
    token = result.stdout.strip()
    if token.count(".") != 2:
        raise RuntimeError("token was not minted")
    return token


def fetch(base: str, path: str, token: str | None) -> tuple[int, object]:
    request = urllib.request.Request(base + path)
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read()
            status = response.status
    except urllib.error.HTTPError as error:
        body = error.read()
        status = error.code
    except Exception as error:  # noqa: BLE001
        return 0, {"error": type(error).__name__, "detail": str(error)}
    text = body.decode("utf-8", errors="replace")
    if not text:
        return status, None
    try:
        return status, json.loads(text)
    except json.JSONDecodeError:
        return status, text[:300]


def normalize(value: object) -> object:
    if isinstance(value, str):
        value = re.sub(r"https?://(?:127\.0\.0\.1|localhost):900[01]", "http://host", value)
        if re.match(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", value):
            value = value.replace(" ", "T").split(".")[0].split("+")[0].rstrip("Z")
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in sorted(value.items())}
    if isinstance(value, list):
        items = [normalize(item) for item in value]
        if items and all(isinstance(item, dict) and "id" in item for item in items):
            items = sorted(items, key=lambda item: str(item.get("id")))
        return items
    return value


CONFIG_FIELDS = {
    "$.version",
    "$.tokenTime",
    "$.oidcProviderName",
    "$.allowedIframeHosts",
    "$.enableOidc",
    "$.production",
    "$.demoStatus",
    "$.totalStorageBytes",
    "$.totalStorageStr",
}


def differ(left: object, right: object, path: str, out: list[str]) -> None:
    if len(out) >= 6 or path in CONFIG_FIELDS:
        return
    if type(left) is not type(right) and not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
        out.append(f"{path}: python={summarize(left)} php={summarize(right)}")
        return
    if isinstance(left, dict) and isinstance(right, dict):
        for key in sorted(set(left) | set(right)):
            if key not in left:
                out.append(f"{path}.{key}: missing on python")
            elif key not in right:
                out.append(f"{path}.{key}: missing on php")
            else:
                differ(left[key], right[key], f"{path}.{key}", out)
            if len(out) >= 6:
                return
        return
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            out.append(f"{path}: length python={len(left)} php={len(right)}")
        for index, (item_left, item_right) in enumerate(zip(left, right, strict=False)):
            differ(item_left, item_right, f"{path}[{index}]", out)
            if len(out) >= 6:
                return
        return
    if left != right:
        out.append(f"{path}: python={summarize(left)} php={summarize(right)}")


def summarize(value: object) -> str:
    text = json.dumps(value, ensure_ascii=False, default=str)
    return text if len(text) <= 120 else text[:117] + "..."


def main() -> None:
    token = token_for_first_user()
    paths = [
        "/api/app/about",
        "/api/app/about/startup-info",
        "/api/app/about/theme",
        "/api/validators/user/name?name=nobody-accuracy-check",
        "/api/auth/oauth",
        "/api/users/self",
        "/api/users/self/ratings",
        "/api/users/self/favorites",
        "/api/users/api-tokens",
        "/api/groups/self",
        "/api/groups/preferences",
        "/api/groups/members?page=1&perPage=10",
        "/api/groups/storage",
        "/api/groups/households?page=1&perPage=10",
        "/api/groups/reports",
        "/api/groups/ai-providers/settings",
        "/api/households/self",
        "/api/households/preferences",
        "/api/households/members?page=1&perPage=10",
        "/api/households/statistics",
        "/api/households/cookbooks?page=1&perPage=10",
        "/api/households/mealplans/today",
        "/api/households/mealplans?page=1&perPage=5",
        "/api/households/mealplans/rules?page=1&perPage=10",
        "/api/households/shopping/lists?page=1&perPage=5",
        "/api/households/shopping/items?page=1&perPage=5",
        "/api/households/webhooks?page=1&perPage=10",
        "/api/households/invitations",
        "/api/households/events/notifications?page=1&perPage=10",
        "/api/households/recipe-actions?page=1&perPage=10",
        "/api/recipes?page=1&perPage=3",
        "/api/recipes/suggestions?limit=3",
        "/api/recipes/timeline/events?page=1&perPage=5",
        "/api/organizers/categories?page=1&perPage=5",
        "/api/organizers/tags?page=1&perPage=5",
        "/api/organizers/tools?page=1&perPage=5",
        "/api/foods?page=1&perPage=5",
        "/api/units?page=1&perPage=5",
        "/api/groups/labels?page=1&perPage=10",
        "/api/comments?page=1&perPage=5",
        "/api/shared/recipes?page=1&perPage=5",
    ]
    same = 0
    matched_paths = []
    status_mismatch = []
    body_mismatch = []
    excluded = []
    for path in paths:
        public = path.startswith("/api/app/") or path.startswith("/api/validators/") or path == "/api/auth/oauth"
        auth = None if public else token
        py_status, py_body = fetch(PY, path, auth)
        php_status, php_body = fetch(PHP, path, auth)
        if "suggestions" in path:
            excluded.append(f"{path}: status python={py_status} php={php_status}; body not compared (unordered sample)")
            continue
        if py_status != php_status:
            status_mismatch.append(f"{path}: python={py_status} php={php_status}")
            continue
        diffs: list[str] = []
        differ(normalize(py_body), normalize(php_body), "$", diffs)
        if diffs:
            body_mismatch.append((path, py_status, diffs))
        else:
            same += 1
            matched_paths.append(f"{path} ({py_status})")

    scored = len(paths) - len(excluded)
    print(
        f"compared={len(paths)} scored={scored} match={same} "
        f"status_mismatch={len(status_mismatch)} body_mismatch={len(body_mismatch)} excluded={len(excluded)}"
    )
    print(f"accuracy={same}/{scored}")
    print("MATCH")
    for line in matched_paths:
        print(line)
    print("EXCLUDED")
    for line in excluded:
        print(line)
    print("STATUS")
    for line in status_mismatch:
        print(line)
    print("BODY")
    for path, status, diffs in body_mismatch:
        print(f"{path} ({status})")
        for diff in diffs:
            print(f"  {diff}")


if __name__ == "__main__":
    main()
