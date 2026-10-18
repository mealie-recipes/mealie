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

SAMPLE_LANGUAGES = ["da", "de", "fr", "nl", "es-ES"]
SAMPLE_STRINGS_PER_LANGUAGE = 25

# Only these project fields are printed; everything else is omitted from the public log
PROJECT_SETTING_KEYS = [
    "exportApprovedOnly",
    "exportTranslatedOnly",
    "exportWithMinApprovalsCount",
    "exportStringsThatPassedWorkflow",
    "skipUntranslatedStrings",
    "skipUntranslatedFiles",
    "translateDuplicates",
    "tmApprovedSuggestionsOnly",
    "hiddenStringsProofreadersAccess",
    "qaCheckIsActive",
    "qaApprovalsCount",
    "qaCheckCategories",
    "normalizePlaceholder",
    "isMtAllowed",
    "autoSubstitution",
    "type",
    "visibility",
    "joinPolicy",
]


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


def main() -> None:
    with urllib.request.urlopen(urllib.request.Request("https://api.crowdin.com/api/v2/user", headers=HEADERS)) as r:
        token_user_id = json.loads(r.read())["data"]["id"]

    section("Project settings (allowlisted)")
    project = get("")["data"]
    for key in PROJECT_SETTING_KEYS:
        print(f"{key} = {project.get(key, '<absent>')}")
    print("all keys:", sorted(project.keys()))
    owner_id = project.get("userId")
    print(f"token user is project owner: {token_user_id == owner_id}")

    # Approvers are shown as anonymous labels; only owner/token-user are marked as such
    labels: dict[int, str] = {}

    def label(user: dict) -> str:
        uid = user["id"]
        if uid not in labels:
            if uid == owner_id:
                labels[uid] = "project-owner"
            elif uid == token_user_id:
                labels[uid] = "token-user"
            else:
                labels[uid] = f"approver-{len(labels) + 1}"
        return labels[uid]

    languages = project["targetLanguageIds"]
    print("target languages:", len(languages))

    section("Files")
    files = get_all("/files")
    for f in files:
        print(f"id={f['id']} path={f['path']}")
    frontend_file = next(
        f for f in files if f["path"].endswith("frontend/app/lang/messages/en-US.json") or f["name"] == "en-US.json"
    )

    section("Approvals by approver (all files x all languages)")
    by_user: Counter[str] = Counter()
    by_year: Counter[str] = Counter()
    by_user_year: Counter[tuple[str, str]] = Counter()
    total = 0
    for f in files:
        for lang in languages:
            for a in get_all("/approvals", fileId=f["id"], languageId=lang):
                username = label(a["user"])
                year = a["createdAt"][:7]
                by_user[username] += 1
                by_year[year] += 1
                by_user_year[(username, year)] += 1
                total += 1
    print(f"total approvals: {total}")
    print(f"distinct approvers: {len(by_user)}")
    for username, count in by_user.most_common(15):
        print(f"  {username}: {count}")
    print("by month:")
    for month, count in sorted(by_year.items()):
        print(f"  {month}: {count}")
    print("top (user, month) clusters:")
    for (username, month), count in by_user_year.most_common(20):
        print(f"  {username} {month}: {count}")

    section("Issue strings (yield) in da")
    strings = get_all("/strings", fileId=frontend_file["id"], filter="yield")
    for s in strings:
        print(f"\nstring id={s['id']} identifier={s['identifier']} text={s['text']!r}")
        approvals = {
            a["translationId"]: label(a["user"]) for a in get_all("/approvals", stringId=s["id"], languageId="da")
        }
        for t in get_all("/translations", stringId=s["id"], languageId="da"):
            print(
                f"  tid={t['id']} rating={t.get('rating')} created={t['createdAt']} "
                f"approved_by={approvals.get(t['id'])} text={t['text']!r}"
            )

    section("Export fallback sample: unapproved strings with multiple translations")
    for lang in SAMPLE_LANGUAGES:
        votes = get_all("/votes", languageId=lang, fileId=frontend_file["id"])
        string_ids = list(dict.fromkeys(v["stringId"] for v in votes if "stringId" in v))
        if not string_ids:
            # Votes may not carry stringId; fall back to translation lookups
            string_ids = list(
                dict.fromkeys(get(f"/translations/{v['translationId']}")["data"]["stringId"] for v in votes[:200])
            )
        print(f"\n--- {lang}: {len(votes)} votes across {len(string_ids)} strings")
        shown = 0
        for sid in string_ids:
            if shown >= SAMPLE_STRINGS_PER_LANGUAGE:
                break
            if get_all("/approvals", stringId=sid, languageId=lang):
                continue
            translations = get_all("/translations", stringId=sid, languageId=lang)
            if len(translations) < 2:
                continue
            identifier = get(f"/strings/{sid}")["data"]["identifier"]
            print(f"  {identifier}")
            for t in sorted(translations, key=lambda t: t["createdAt"]):
                print(f"    rating={t.get('rating')} created={t['createdAt']} text={t['text']!r}")
            shown += 1

    section("Votes per language (frontend file), net negative on approved translations")
    for lang in SAMPLE_LANGUAGES:
        approved = {a["translationId"] for a in get_all("/approvals", fileId=frontend_file["id"], languageId=lang)}
        net: defaultdict[int, int] = defaultdict(int)
        for v in get_all("/votes", languageId=lang, fileId=frontend_file["id"]):
            net[v["translationId"]] += 1 if v["mark"] == "up" else -1
        contested = [tid for tid, score in net.items() if tid in approved and score < 0]
        print(
            f"  {lang}: approved={len(approved)} voted_translations={len(net)} net_negative_approved={len(contested)}"
        )


if __name__ == "__main__":
    main()
