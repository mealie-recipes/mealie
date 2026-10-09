"""Send the same requests to the Python and Java backends and compare the responses.

Both backends must be running against the same database. Before comparing anything, the script checks that:
  * both backends report the same DB engine (Python's /api/admin/about vs Java's /api/java/health),
  * both accept the token and resolve it to the same user.

Cases come from dev/rebuild/diff_cases.json, or a single ad-hoc case can be given on the command line:

    uv run python dev/rebuild/diff_test.py                       # all cases in diff_cases.json
    uv run python dev/rebuild/diff_test.py GET /api/foods        # one ad-hoc case
    uv run python dev/rebuild/diff_test.py --expect-engine postgres --report out.json

Each case compares the status code and the JSON body (ignoring key order). Fields that legitimately differ can be
ignored with dotted paths where "*" matches any key or list index, e.g. "items.*.updatedAt".

Only use read-only requests unless you know what you are doing: both backends share one database, so a POST is
applied twice.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_CASES = Path(__file__).parent / "diff_cases.json"
MISSING = object()


@dataclass
class Response:
    status: int
    content_type: str
    body: bytes

    def json(self) -> Any:
        if "json" not in self.content_type:
            return MISSING
        try:
            return json.loads(self.body)
        except ValueError:
            return MISSING


@dataclass
class Case:
    method: str
    path: str
    name: str = ""
    body: Any = None
    ignore: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return self.name or f"{self.method} {self.path}"


def request(base: str, method: str, path: str, token: str | None, body: Any = None) -> Response:
    headers = {"Accept": "application/json"}
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(base.rstrip("/") + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return Response(resp.status, resp.headers.get("Content-Type", ""), resp.read())
    except urllib.error.HTTPError as e:
        return Response(e.code, e.headers.get("Content-Type", ""), e.read())


def login(base: str, username: str, password: str) -> str:
    form = urllib.parse.urlencode({"username": username, "password": password}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/api/auth/token", data=form, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)["access_token"]
    except urllib.error.HTTPError as e:
        sys.exit(
            f"login as {username} on {base} failed (HTTP {e.code}). "
            "Pass an admin token with --token / MEALIE_TOKEN, or credentials with --username/--password."
        )


def strip_ignored(value: Any, path: list[str]) -> Any:
    """Return a copy of value without the field at the dotted path ("*" matches any key or index)."""
    if not path:
        return value
    head, rest = path[0], path[1:]
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if head in ("*", k):
                if rest:
                    out[k] = strip_ignored(v, rest)
                # else: this is the ignored leaf, drop it
            else:
                out[k] = v
        return out
    if isinstance(value, list):
        out_list = []
        for i, v in enumerate(value):
            if head in ("*", str(i)):
                if rest:
                    out_list.append(strip_ignored(v, rest))
                else:
                    out_list.append(None)  # keep positions stable for the rest of the list
            else:
                out_list.append(v)
        return out_list
    return value


def differences(a: Any, b: Any, path: str = "$") -> list[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for key in sorted(set(a) | set(b)):
            sub = f"{path}.{key}"
            if key not in a:
                out.append(f"{sub}: only in java ({short(b[key])})")
            elif key not in b:
                out.append(f"{sub}: only in python ({short(a[key])})")
            else:
                out.extend(differences(a[key], b[key], sub))
        return out
    if isinstance(a, list) and isinstance(b, list):
        out = []
        if len(a) != len(b):
            out.append(f"{path}: length python={len(a)} java={len(b)}")
        for i, (x, y) in enumerate(zip(a, b, strict=False)):
            out.extend(differences(x, y, f"{path}[{i}]"))
        return out
    if not same_scalar(a, b):
        return [f"{path}: python={short(a)} java={short(b)}"]
    return []


def same_scalar(a: Any, b: Any) -> bool:
    # bool is an int subclass in Python, so true must not equal 1. 1 and 1.0 are the same JSON number to a client.
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, int | float) and isinstance(b, int | float):
        return a == b
    return type(a) is type(b) and a == b


def short(value: Any, limit: int = 80) -> str:
    text = json.dumps(value) if value is not MISSING else "<not json>"
    return text if len(text) <= limit else text[: limit - 3] + "..."


def compare(case: Case, py: Response, java: Response, global_ignore: list[str]) -> list[str]:
    problems = []
    if py.status != java.status:
        problems.append(f"status: python={py.status} java={java.status}")
    a, b = py.json(), java.json()
    if a is MISSING or b is MISSING:
        if (a is MISSING) != (b is MISSING):
            problems.append(f"body: python json={a is not MISSING} java json={b is not MISSING}")
        elif py.body != java.body:
            problems.append("body: non-JSON bodies differ")
        return problems
    for path in [*global_ignore, *case.ignore]:
        parts = path.split(".")
        a, b = strip_ignored(a, parts), strip_ignored(b, parts)
    problems.extend(differences(a, b))
    return problems


def preflight(args: argparse.Namespace, token: str) -> tuple[list[str], str | None]:
    """Check both backends are up, on the same engine, and agree on who the token belongs to."""
    problems = []

    java = request(args.java, "GET", "/api/java/health", token)
    health = java.json()
    if java.status != 200 or not isinstance(health, dict):
        return [f"java health: HTTP {java.status} {java.body[:200]!r}"], None
    java_engine = health.get("dbEngine")
    auth = health.get("auth") or {}
    if not auth.get("authenticated"):
        problems.append(f"java rejected the token: {auth.get('detail')}")

    py_engine = None
    about = request(args.python, "GET", "/api/admin/about", token)
    if about.status == 200:
        py_engine = about.json().get("dbType")
    else:
        problems.append(f"python /api/admin/about: HTTP {about.status} (the diff test needs an admin token)")

    if py_engine is not None and py_engine != java_engine:
        problems.append(f"engine mismatch: python={py_engine} java={java_engine}")
    if args.expect_engine and java_engine != args.expect_engine:
        problems.append(f"expected engine {args.expect_engine}, java is on {java_engine}")

    me = request(args.python, "GET", "/api/users/self", token)
    py_user = me.json().get("id") if me.status == 200 else None
    if py_user is None:
        problems.append(f"python /api/users/self: HTTP {me.status}")
    elif auth.get("authenticated") and py_user != auth.get("userId"):
        problems.append(f"token resolves to different users: python={py_user} java={auth.get('userId')}")

    return problems, java_engine


def load_cases(args: argparse.Namespace) -> list[Case]:
    if args.adhoc:
        if len(args.adhoc) < 2:
            sys.exit("ad-hoc case needs METHOD PATH [JSON_BODY]")
        method, path, *rest = args.adhoc
        body = json.loads(rest[0]) if rest else None
        return [Case(method=method.upper(), path=path, body=body)]
    data = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    return [
        Case(
            method=c.get("method", "GET").upper(),
            path=c["path"],
            name=c.get("name", ""),
            body=c.get("body"),
            ignore=c.get("ignore", []),
        )
        for c in data.get("cases", [])
    ]


def say(message: str = "") -> None:
    sys.stdout.write(message + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("adhoc", nargs="*", metavar="METHOD PATH [BODY]", help="run one ad-hoc case instead")
    parser.add_argument("--python", default=os.getenv("DIFF_PYTHON_URL", "http://localhost:9000"))
    parser.add_argument("--java", default=os.getenv("DIFF_JAVA_URL", "http://localhost:9100"))
    parser.add_argument("--token", default=os.getenv("MEALIE_TOKEN"), help="defaults to logging in on Python")
    parser.add_argument("--username", default=os.getenv("DIFF_USERNAME", "changeme@example.com"))
    parser.add_argument("--password", default=os.getenv("DIFF_PASSWORD", "MyPassword"))
    parser.add_argument("--cases", default=str(DEFAULT_CASES))
    parser.add_argument("--ignore", action="append", default=[], help="dotted path to ignore in every case")
    parser.add_argument("--expect-engine", choices=["sqlite", "postgres"])
    parser.add_argument("--report", help="write a JSON summary here")
    args = parser.parse_args()

    token = args.token or login(args.python, args.username, args.password)

    problems, engine = preflight(args, token)
    say(f"engine: {engine}")
    if problems:
        say("PREFLIGHT FAILED")
        for p in problems:
            say(f"  - {p}")
        return 1
    say("preflight: both backends up, same engine, token accepted by both for the same user")

    cases = load_cases(args)
    results = []
    for case in cases:
        py = request(args.python, case.method, case.path, token, case.body)
        java = request(args.java, case.method, case.path, token, case.body)
        problems = compare(case, py, java, args.ignore)
        results.append({"case": case.label, "passed": not problems, "problems": problems})
        say(f"{'PASS' if not problems else 'FAIL'}  {case.label}")
        for p in problems[:20]:
            say(f"        {p}")
        if len(problems) > 20:
            say(f"        ... {len(problems) - 20} more")

    passed = sum(r["passed"] for r in results)
    say(f"\n{passed}/{len(results)} cases passed on {engine}")
    if not results:
        say("(no cases yet: add them to dev/rebuild/diff_cases.json as endpoints are migrated)")

    if args.report:
        summary = {"engine": engine, "passed": passed, "total": len(results), "results": results}
        Path(args.report).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
