#!/usr/bin/env python3
"""
seed_mealie_recipes.py — Delete all existing recipes, then seed N recipes
from RAW_recipes.csv with real Food.com tags.

Usage:
    python3 seed_mealie_recipes.py \
        --csv /path/to/RAW_recipes.csv \
        --mealie-url http://127.0.0.1:30090 \
        --email abc@gmail.com \
        --password 12345678 \
        --count 150
"""
import argparse
import ast
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd

NOISE_TAGS = {
    "time-to-make", "course", "main-ingredient", "cuisine", "preparation",
    "occasion", "dietary", "equipment", "technique", "for-large-groups",
    "number-of-servings", "weeknight", "from-scratch",
}
NOISE_PREFIXES = (
    "60-minutes-or-less", "30-minutes-or-less", "15-minutes-or-less",
    "4-hours-or-less", "1-day-or-more",
)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_tags(raw) -> list[str]:
    if pd.isna(raw):
        return []
    if isinstance(raw, list):
        return [str(t) for t in raw]
    try:
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, list):
            return [str(t) for t in parsed]
    except Exception:
        pass
    return []


def useful_tags(raw_tags: list[str]) -> list[str]:
    result = []
    for tag in raw_tags:
        t = tag.strip()
        if not t:
            continue
        if t in NOISE_TAGS:
            continue
        if any(t.startswith(p) for p in NOISE_PREFIXES):
            continue
        result.append(t)
    return result


def mealie_request(method: str, url: str, data=None, token: str | None = None):
    body = json.dumps(data).encode() if data is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            body_text = json.loads(raw)
        except Exception:
            body_text = raw.decode(errors="replace")
        return e.code, body_text


def get_token(base_url: str, email: str, password: str) -> str:
    for attempt in range(12):
        req = urllib.request.Request(
            f"{base_url}/api/auth/token",
            data=urllib.parse.urlencode({
                "username": email, "password": password, "grant_type": "password"
            }).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())["access_token"]
        except Exception as e:
            print(f"  Mealie not ready (attempt {attempt + 1}/12): {e}")
            time.sleep(10)
    print("ERROR: Could not authenticate with Mealie — aborting")
    sys.exit(1)


def delete_all_recipes(base_url: str, token: str):
    page = 1
    deleted = 0
    while True:
        status, data = mealie_request(
            "GET", f"{base_url}/api/recipes?page={page}&perPage=50", token=token
        )
        if status != 200:
            break
        items = data.get("items", [])
        if not items:
            break
        for r in items:
            slug = r.get("slug") or r.get("id")
            if slug:
                mealie_request("DELETE", f"{base_url}/api/recipes/{slug}", token=token)
                deleted += 1
        if len(items) < 50:
            break
        page += 1
    print(f"  Deleted {deleted} existing recipes.")


def load_recipes(csv_path: str, count: int) -> list[dict]:
    df = pd.read_csv(csv_path, usecols=["name", "id", "minutes", "tags"])
    df = df.dropna(subset=["name", "tags"])
    df["minutes"] = pd.to_numeric(df["minutes"], errors="coerce").fillna(999)
    df = df[(df["minutes"] >= 5) & (df["minutes"] <= 120)]
    df["parsed_tags"] = df["tags"].apply(parse_tags)
    df["useful"] = df["parsed_tags"].apply(useful_tags)
    df = df[df["useful"].apply(len) >= 3]
    df = df.sort_values(by=df["useful"].apply(len), key=lambda s: s, ascending=False)
    df = df.head(count * 3).sample(n=min(count, len(df)), random_state=42)
    result = []
    for _, row in df.iterrows():
        result.append({
            "name": str(row["name"]).strip()[:255],
            "tags": row["useful"][:10],
        })
    return result


def seed(base_url: str, token: str, recipes: list[dict]) -> tuple[int, int, int]:
    created = tagged = failed = 0
    for i, recipe in enumerate(recipes, 1):
        name = recipe["name"]
        tags = recipe["tags"]

        # Step 1: create recipe
        status, data = mealie_request("POST", f"{base_url}/api/recipes", {"name": name}, token)
        if status not in (200, 201):
            print(f"  [{i}] SKIP create '{name[:40]}': {status} {data}")
            failed += 1
            continue
        slug = data if isinstance(data, str) else data.get("slug", "")
        if not slug:
            failed += 1
            continue
        created += 1

        # Step 2: fetch full object (required so PATCH doesn't 400)
        status, full = mealie_request("GET", f"{base_url}/api/recipes/{slug}", token=token)
        if status != 200:
            print(f"  [{i}] SKIP get '{slug}': {status}")
            failed += 1
            continue

        # Step 3: patch with tags
        full["tags"] = [{"name": t, "slug": slugify(t)} for t in tags]
        status, _ = mealie_request("PATCH", f"{base_url}/api/recipes/{slug}", full, token)
        if status in (200, 201):
            tagged += 1
            if i % 25 == 0:
                print(f"  progress: {i}/{len(recipes)} (tagged {tagged})")
        else:
            print(f"  [{i}] PATCH failed '{slug}': {status}")
            failed += 1

    return created, tagged, failed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--mealie-url", default="http://127.0.0.1:30090")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--count", type=int, default=150)
    args = parser.parse_args()

    base_url = args.mealie_url.rstrip("/")

    print("Authenticating with Mealie...")
    token = get_token(base_url, args.email, args.password)
    print("Authenticated.")

    print("Deleting existing recipes (clean slate)...")
    delete_all_recipes(base_url, token)

    print(f"Loading {args.count} recipes from {args.csv}...")
    recipes = load_recipes(args.csv, args.count)
    print(f"  Selected {len(recipes)} recipes with useful tags.")

    print("Seeding recipes into Mealie...")
    created, tagged, failed = seed(base_url, token, recipes)

    print()
    print(f"=== Seed complete: created={created}, tagged={tagged}, failed={failed} ===")


if __name__ == "__main__":
    main()
