# ruff: noqa: T201
"""Temporary read-only probe of Crowdin project state (issue #8721). Makes GET requests only.

Output is public (Actions logs): no usernames, user ids, or free-form project fields are printed.
"""

import json
import os
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

PROJECT_ID = "451976"
BASE_URL = f"https://api.crowdin.com/api/v2/projects/{PROJECT_ID}"
HEADERS = {"Authorization": f"Bearer {os.environ['CROWDIN_API_KEY']}"}

CURRENT_FRONTEND_FILE_ID = 100  # /mealie-next/frontend/app/lang/messages/en-US.json
LEGACY_FRONTEND_FILE_ID = 82  # /mealie-next/frontend/lang/messages/en-US.json (pre-Nuxt 4 path)
YIELD_IDENTIFIERS = ["recipe.yield-text", "recipe.recipe-yield", "recipe.recipe-yield-text", "recipe.yield"]
SAMPLE_LANGUAGES = ["da", "de", "fr", "nl", "es-ES"]
SAMPLE_STRINGS_PER_LANGUAGE = 15


def get(path: str, **params) -> dict:
    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS)) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"GET {path} {params} -> {e.code}: {e.read().decode()[:300]}") from e
    raise RuntimeError("unreachable")


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


def main() -> None:
    languages = get("")["data"]["targetLanguageIds"]
    strings = {s["id"]: s["identifier"] for s in get_all("/strings", fileId=CURRENT_FRONTEND_FILE_ID)}
    string_ids = {identifier: sid for sid, identifier in strings.items()}

    def shapes() -> None:
        section("Response shapes (key names only)")
        print("vote:", sorted(get_all("/votes", languageId="da", fileId=CURRENT_FRONTEND_FILE_ID)[0].keys()))
        print("approval:", sorted(get_all("/approvals", languageId="da", fileId=CURRENT_FRONTEND_FILE_ID)[0].keys()))
        lang_translations = get("/languages/da/translations", fileId=CURRENT_FRONTEND_FILE_ID, limit=1)["data"]
        print("language translation:", sorted(lang_translations[0]["data"].keys()))

    def legacy_file() -> None:
        section("Legacy file 82 vs current file 100: translations created in 2026, per language")
        legacy_total = current_total = 0
        for lang in languages:
            counts = []
            for file_id in (LEGACY_FRONTEND_FILE_ID, CURRENT_FRONTEND_FILE_ID):
                items = get_all(f"/languages/{lang}/translations", fileId=file_id)
                counts.append(sum(1 for t in items if (t.get("createdAt") or "") >= "2026-01-01"))
            legacy_total += counts[0]
            current_total += counts[1]
            if counts[0]:
                print(f"  {lang}: legacy={counts[0]} current={counts[1]}")
        print(f"totals: legacy={legacy_total} current={current_total}")

    def yield_strings() -> None:
        section("Issue strings (yield) in da, current file")
        for identifier in YIELD_IDENTIFIERS:
            sid = string_ids[identifier]
            approvals = {a["translationId"] for a in get_all("/approvals", stringId=sid, languageId="da")}
            print(f"\n{identifier} (string id={sid})")
            for t in get_all("/translations", stringId=sid, languageId="da"):
                print(
                    f"  tid={t['id']} rating={t.get('rating')} created={t['createdAt']} "
                    f"approved={t['id'] in approvals} text={t['text']!r}"
                )

    def export_pick() -> None:
        section("Which translation does the API pick for unapproved strings with alternatives?")
        for lang in SAMPLE_LANGUAGES:
            picked = {
                t["stringId"]: t for t in get_all(f"/languages/{lang}/translations", fileId=CURRENT_FRONTEND_FILE_ID)
            }
            approved_sids = {
                a["stringId"] for a in get_all("/approvals", fileId=CURRENT_FRONTEND_FILE_ID, languageId=lang)
            }
            outcome: Counter[str] = Counter()
            checked = 0
            print(f"\n--- {lang}: {len(picked)} strings, {len(approved_sids)} approved")
            for sid, chosen in picked.items():
                if sid in approved_sids:
                    continue
                if (
                    checked >= 300
                    or sum(v for k, v in outcome.items() if k != "newest+top") >= SAMPLE_STRINGS_PER_LANGUAGE
                ):
                    break
                checked += 1
                translations = get_all("/translations", stringId=sid, languageId=lang)
                if len(translations) < 2:
                    continue
                newest = max(translations, key=lambda t: t["createdAt"])
                top = max(translations, key=lambda t: (t.get("rating") or 0, t["createdAt"]))
                tid = chosen.get("translationId")
                if tid == newest["id"] == top["id"]:
                    kind = "newest+top"
                elif tid == newest["id"]:
                    kind = "newest"
                elif tid == top["id"]:
                    kind = "top-voted"
                else:
                    kind = "other"
                outcome[kind] += 1
                if kind != "newest+top":
                    print(f"  {strings.get(sid)} -> picked={kind} text={chosen.get('text')!r}")
                    for t in sorted(translations, key=lambda t: t["createdAt"]):
                        print(f"    rating={t.get('rating')} created={t['createdAt']} text={t['text']!r}")
            print(f"  checked={checked} outcome counts: {dict(outcome)}")

    def contested() -> None:
        section("Approved translations with net-negative votes, current file, all languages")
        total = 0
        for lang in languages:
            approved = {
                a["translationId"] for a in get_all("/approvals", fileId=CURRENT_FRONTEND_FILE_ID, languageId=lang)
            }
            net: defaultdict[int, int] = defaultdict(int)
            for v in get_all("/votes", languageId=lang, fileId=CURRENT_FRONTEND_FILE_ID):
                net[v["translationId"]] += 1 if v["mark"] == "up" else -1
            count = sum(1 for tid, score in net.items() if tid in approved and score < 0)
            total += count
            print(f"  {lang}: approved={len(approved)} voted={len(net)} net_negative_approved={count}")
        print(f"total net-negative approved: {total}")

    for step, fn in [
        ("shapes", shapes),
        ("yield strings", yield_strings),
        ("export pick", export_pick),
        ("contested", contested),
        ("legacy file", legacy_file),
    ]:
        safe(step, fn)


if __name__ == "__main__":
    main()
