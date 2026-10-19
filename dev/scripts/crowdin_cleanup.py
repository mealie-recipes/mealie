# ruff: noqa: T201, C901
"""One-time Crowdin approval cleanup (issue #8721).

Dry run unless CROWDIN_CLEANUP_APPLY=true. Steps:
1. Copy translations that only exist (newer) in the legacy frontend file into the current file
2. Remove every approval, file by file
3. Re-approve two Danish canaries so the upcoming guard job can be verified
4. Read back the remaining approvals (expect exactly the canaries)

Output is public (Actions logs): no usernames, user ids, or download URLs are printed.
"""

import json
import os
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

PROJECT_ID = "451976"
BASE_URL = f"https://api.crowdin.com/api/v2/projects/{PROJECT_ID}"
HEADERS = {"Authorization": f"Bearer {os.environ['CROWDIN_API_KEY']}", "Content-Type": "application/json"}
APPLY = os.environ.get("CROWDIN_CLEANUP_APPLY", "").lower() == "true"
RUN_SALVAGE = False  # completed in run 39183780164

CURRENT_FILE_ID = 100  # /mealie-next/frontend/app/lang/messages/en-US.json
LEGACY_FILE_ID = 82  # /mealie-next/frontend/lang/messages/en-US.json (pre-Nuxt 4 path)

# (languageId, identifier) -> text: salvaged translations corrected during review
SALVAGE_OVERRIDES = {
    ("it", "general.a-name-is-required"): "È necessario un nome",
}

# (languageId, identifier, translationId): approved imports the community has voted against
CANARIES = [
    ("da", "recipe.yield-text", 439352),
    ("da", "recipe.recipe-yield", 439558),
]


def request(method: str, path: str, body: dict | None = None, **params) -> dict:
    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
            with urllib.request.urlopen(req) as r:
                raw = r.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"{method} {path} {params} -> {e.code}: {e.read().decode()[:300]}") from e
    raise RuntimeError("unreachable")


def get_all(path: str, **params) -> list[dict]:
    items: list[dict] = []
    offset = 0
    while True:
        page = request("GET", path, limit=500, offset=offset, **params)["data"]
        items.extend(p["data"] for p in page)
        if len(page) < 500:
            return items
        offset += 500


def section(title: str) -> None:
    print(f"\n===== {title} =====", flush=True)


def salvage(languages: list[str]) -> None:
    section("1. Salvage newer translations from legacy file 82")
    strings = {f: {s["id"]: s for s in get_all("/strings", fileId=f)} for f in (LEGACY_FILE_ID, CURRENT_FILE_ID)}
    current_by_identifier = {s["identifier"]: s for s in strings[CURRENT_FILE_ID].values()}
    added = skipped = failed = 0
    for lang in languages:
        picked = {
            f: {t["stringId"]: t for t in get_all(f"/languages/{lang}/translations", fileId=f)}
            for f in (LEGACY_FILE_ID, CURRENT_FILE_ID)
        }
        for sid, legacy in picked[LEGACY_FILE_ID].items():
            legacy_string = strings[LEGACY_FILE_ID].get(sid)
            if not legacy_string or legacy_string["identifier"] not in current_by_identifier:
                continue
            current_string = current_by_identifier[legacy_string["identifier"]]
            current = picked[CURRENT_FILE_ID].get(current_string["id"])
            # Only copy fixes made in the dead file after the current file's translation
            if (
                legacy_string["text"] != current_string["text"]
                or current is None
                or current["text"] == legacy["text"]
                or legacy["createdAt"] <= current["createdAt"]
            ):
                continue
            text = SALVAGE_OVERRIDES.get((lang, legacy_string["identifier"]), legacy["text"])
            label = f"{lang} {legacy_string['identifier']}: {current['text']!r} -> {text!r}"
            existing = get_all("/translations", stringId=current_string["id"], languageId=lang)
            if any(t["text"] == text for t in existing):
                skipped += 1
                print(f"  skip (already an alternative in current file) {label}")
                continue
            if not APPLY:
                added += 1
                print(f"  would add {label}")
                continue
            try:
                request(
                    "POST",
                    "/translations",
                    {"stringId": current_string["id"], "languageId": lang, "text": text},
                )
                added += 1
                print(f"  added {label}")
            except RuntimeError as e:
                failed += 1
                print(f"  FAILED {label}: {e}")
    print(f"salvage: {'added' if APPLY else 'would add'}={added} skipped={skipped} failed={failed}")


def remove_approvals(files: list[dict], languages: list[str]) -> None:
    section("2. Remove all approvals")
    # stringId -> languages with an approval; removal by fileId only works for asset files, so go string by string
    approved: defaultdict[int, set[str]] = defaultdict(set)
    total = 0
    for f in files:
        count = 0
        for lang in languages:
            for a in get_all("/approvals", fileId=f["id"], languageId=lang):
                approved[a["stringId"]].add(lang)
                count += 1
        total += count
        print(f"  file {f['id']} {f['path']}: {count} approvals")
    print(f"total before: {total} across {len(approved)} strings")
    if not APPLY:
        return

    string_ids = list(approved)
    first = string_ids[0]
    request("DELETE", "/approvals", stringId=first)
    for lang in sorted(approved[first])[:2]:
        if get_all("/approvals", stringId=first, languageId=lang):
            raise RuntimeError(f"removing approvals for string {first} left {lang} approved; aborting")
    print(f"  verified removal on string {first}; continuing")

    # Crowdin allows 20 simultaneous requests per account; stay well under it
    with ThreadPoolExecutor(max_workers=8) as pool:
        for i, _ in enumerate(pool.map(lambda sid: request("DELETE", "/approvals", stringId=sid), string_ids[1:]), 2):
            if i % 250 == 0:
                print(f"  removed {i}/{len(string_ids)}", flush=True)
    print(f"  removed {len(string_ids)}/{len(string_ids)}")


def reapprove_canaries() -> None:
    section("3. Re-approve canaries")
    for lang, identifier, tid in CANARIES:
        translation = request("GET", f"/translations/{tid}")["data"]
        print(f"  {lang} {identifier} tid={tid} rating={translation.get('rating')} text={translation['text']!r}")
        if APPLY:
            request("POST", "/approvals", {"translationId": tid})
            print("    approved")


def read_back(files: list[dict], languages: list[str]) -> None:
    section("4. Remaining approvals")
    remaining: defaultdict[int, list[tuple[str, int]]] = defaultdict(list)
    for f in files:
        for lang in languages:
            for a in get_all("/approvals", fileId=f["id"], languageId=lang):
                remaining[f["id"]].append((lang, a["translationId"]))
    total = sum(len(v) for v in remaining.values())
    for file_id, approvals in remaining.items():
        print(f"  file {file_id}: {len(approvals)}")
    expected = {(lang, tid) for lang, _, tid in CANARIES}
    actual = {pair for approvals in remaining.values() for pair in approvals}
    print(f"total remaining: {total}; matches canaries exactly: {actual == expected}")


def main() -> None:
    print(f"MODE: {'APPLY' if APPLY else 'DRY RUN'}")
    languages = request("GET", "")["data"]["targetLanguageIds"]
    files = [f for f in get_all("/files") if f["path"].endswith(".json")]

    if RUN_SALVAGE:
        salvage(languages)
    remove_approvals(files, languages)
    reapprove_canaries()
    if APPLY:
        read_back(files, languages)


if __name__ == "__main__":
    main()
