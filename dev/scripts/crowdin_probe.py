# ruff: noqa: T201, C901
"""Temporary probe of Crowdin project state (issue #8721). Never modifies the project.

Only GET requests, plus file translation builds (POST .../translations/builds/files/{id}), which
generate a downloadable export without changing any project data.

Output is public (Actions logs): no usernames, user ids, or download URLs are printed.
"""

import json
import os
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

PROJECT_ID = "451976"
BASE_URL = f"https://api.crowdin.com/api/v2/projects/{PROJECT_ID}"
HEADERS = {"Authorization": f"Bearer {os.environ['CROWDIN_API_KEY']}", "Content-Type": "application/json"}

CURRENT_FILE_ID = 100  # /mealie-next/frontend/app/lang/messages/en-US.json
LEGACY_FILE_ID = 82  # /mealie-next/frontend/lang/messages/en-US.json (pre-Nuxt 4 path)
EXAMPLES_PER_CATEGORY = 3
EXPORT_RULE_LANGUAGES_MAX = 6


def request(method: str, url: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
            with urllib.request.urlopen(req) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                time.sleep(2**attempt)
                continue
            path = url.split("?")[0].replace(BASE_URL, "")
            raise RuntimeError(f"{method} {path} -> {e.code}: {e.read().decode()[:300]}") from e
    raise RuntimeError("unreachable")


def get(path: str, **params) -> dict:
    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return request("GET", url)


def get_all(path: str, **params) -> list[dict]:
    items: list[dict] = []
    offset = 0
    while True:
        page = get(path, limit=500, offset=offset, **params)["data"]
        items.extend(p["data"] for p in page)
        if len(page) < 500:
            return items
        offset += 500


def section(title: str) -> None:
    print(f"\n===== {title} =====", flush=True)


def safe(step: str, fn) -> None:
    """Run one probe step; a failure is printed and the remaining steps still run."""
    try:
        fn()
    except Exception as e:
        print(f"!! {step} failed: {type(e).__name__}: {e}", flush=True)


def lookup(tree: dict, identifier: str) -> str | None:
    """Resolve a dotted identifier ("recipe.yield-text") in an exported nested JSON file."""
    node: object = tree
    for part in identifier.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, str) else None


def main() -> None:
    languages = get("")["data"]["targetLanguageIds"]
    strings = {f: {s["id"]: s for s in get_all("/strings", fileId=f)} for f in (LEGACY_FILE_ID, CURRENT_FILE_ID)}
    current_by_identifier = {s["identifier"]: s for s in strings[CURRENT_FILE_ID].values()}

    def approvals_by_file() -> None:
        section("Approvals per file (all languages)")
        for f in get_all("/files"):
            total = sum(len(get_all("/approvals", fileId=f["id"], languageId=lang)) for lang in languages)
            print(f"  file {f['id']} {f['path']}: {total}")

    def salvage() -> None:
        section("Legacy file 82 -> current file 100 salvage candidates")
        print(f"strings: legacy={len(strings[LEGACY_FILE_ID])} current={len(strings[CURRENT_FILE_ID])}")
        legacy_only_ids = {s["identifier"] for s in strings[LEGACY_FILE_ID].values()} - set(current_by_identifier)
        print(f"identifiers only in legacy (removed keys, ignored): {len(legacy_only_ids)}")
        totals: Counter[str] = Counter()
        providers: Counter[str] = Counter()
        examples: defaultdict[str, list[str]] = defaultdict(list)
        for lang in languages:
            picked = {
                f: {t["stringId"]: t for t in get_all(f"/languages/{lang}/translations", fileId=f)}
                for f in (LEGACY_FILE_ID, CURRENT_FILE_ID)
            }
            counts: Counter[str] = Counter()
            for sid, legacy in picked[LEGACY_FILE_ID].items():
                legacy_string = strings[LEGACY_FILE_ID].get(sid)
                if not legacy_string or legacy_string["identifier"] not in current_by_identifier:
                    continue
                current_string = current_by_identifier[legacy_string["identifier"]]
                current = picked[CURRENT_FILE_ID].get(current_string["id"])
                if legacy_string["text"] != current_string["text"]:
                    kind = "source-changed"
                elif current is None:
                    kind = "missing-in-current"
                elif current["text"] == legacy["text"]:
                    kind = "identical"
                elif legacy["createdAt"] > current["createdAt"]:
                    kind = "newer-in-legacy"
                else:
                    kind = "older-in-legacy"
                counts[kind] += 1
                if kind in ("missing-in-current", "newer-in-legacy"):
                    pre = "pre-translated" if legacy.get("isPreTranslated") else "human"
                    providers[f"{kind}/{legacy.get('provider') or 'none'}/{pre}"] += 1
                    if len(examples[kind]) < EXAMPLES_PER_CATEGORY:
                        examples[kind].append(
                            f"{lang} {legacy_string['identifier']} legacy={legacy['text']!r} "
                            f"({legacy['createdAt'][:10]}) current={current['text'] if current else None!r}"
                        )
            totals.update(counts)
            print(f"  {lang}: {dict(counts)}")
        print(f"totals: {dict(totals)}")
        print("candidate provenance (category/provider/pre-translated):")
        for key, count in providers.most_common():
            print(f"  {key}: {count}")
        for kind, lines in examples.items():
            print(f"examples {kind}:")
            for line in lines:
                print(f"  {line}")

    def export_rule() -> None:
        section("Export rule: which translation is exported for unapproved strings?")
        shape = get("/translations", fileId=CURRENT_FILE_ID, languageId="da", limit=1)["data"]
        keys = sorted(shape[0]["data"].keys()) if shape else []
        print("string translation (by file) keys:", keys)
        if "stringId" not in keys:
            print("no stringId on file-scoped translation listing; cannot group cheaply, skipping")
            return
        tested = 0
        outcome: Counter[str] = Counter()
        for file_id in (CURRENT_FILE_ID, LEGACY_FILE_ID):
            for lang in languages:
                if tested >= EXPORT_RULE_LANGUAGES_MAX:
                    break
                approved = {a["stringId"] for a in get_all("/approvals", fileId=file_id, languageId=lang)}
                by_string: defaultdict[int, list[dict]] = defaultdict(list)
                for t in get_all("/translations", fileId=file_id, languageId=lang):
                    by_string[t["stringId"]].append(t)
                cases = []
                for sid, translations in by_string.items():
                    if sid in approved or len(translations) < 2:
                        continue
                    newest = max(translations, key=lambda t: t["createdAt"])
                    top = max(translations, key=lambda t: (t.get("rating") or 0, t["createdAt"]))
                    if newest["id"] != top["id"] and newest["text"] != top["text"]:
                        cases.append((sid, newest, top))
                if not cases:
                    continue
                tested += 1
                build = request("POST", f"{BASE_URL}/translations/builds/files/{file_id}", {"targetLanguageId": lang})[
                    "data"
                ]
                with urllib.request.urlopen(build["url"]) as r:
                    exported = json.loads(r.read())
                print(f"\n--- file {file_id} {lang}: {len(cases)} strings where newest != top-voted")
                for sid, newest, top in cases:
                    identifier = strings[file_id][sid]["identifier"]
                    text = lookup(exported, identifier)
                    kind = "newest" if text == newest["text"] else "top-voted" if text == top["text"] else "other"
                    outcome[kind] += 1
                    print(
                        f"  {identifier}: exported={kind} | newest={newest['text']!r} ({newest.get('rating')}) "
                        f"| top={top['text']!r} ({top.get('rating')})"
                    )
        print(f"\nexport rule outcome: {dict(outcome)}")

    for step, fn in [("export rule", export_rule), ("salvage", salvage), ("approvals by file", approvals_by_file)]:
        safe(step, fn)


if __name__ == "__main__":
    main()
