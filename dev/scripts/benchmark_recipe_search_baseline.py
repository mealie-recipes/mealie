"""Measure old recipe search against an existing isolated benchmark database."""

import argparse
import concurrent.futures
import json
import logging
import math
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=100)
    parser.add_argument("--clients", type=int, default=5)
    args = parser.parse_args()
    if "search-bench" not in os.environ.get("DATA_DIR", ""):
        parser.error("Use an isolated search-bench DATA_DIR with an existing fixture")
    source = args.source.resolve()
    sys.path.insert(0, str(source))
    os.chdir(source)
    from fastapi.testclient import TestClient
    from sqlalchemy import func, select

    import mealie
    from mealie.app import app
    from mealie.core.config import get_app_settings
    from mealie.db.db_setup import SessionLocal, engine
    from mealie.db.models.recipe.recipe import RecipeModel

    assert str(Path(mealie.__file__).resolve()).startswith(str(source) + os.sep)
    logging.disable(logging.CRITICAL)
    settings = get_app_settings()
    with SessionLocal() as session:
        recipes = session.scalar(select(func.count()).select_from(RecipeModel))
    client = TestClient(app)
    response = client.post(
        "/api/auth/token", data={"username": settings._DEFAULT_EMAIL, "password": settings._DEFAULT_PASSWORD}
    )
    response.raise_for_status()
    headers = {"Authorization": "Bearer " + response.json()["access_token"]}
    client.close()
    corpus = [
        ("pork lettuce wrap", "all"),
        ('"lettuce cups" pork', "all"),
        ("+pork lettuce wrap", "all"),
        ("pork -cilantro", "all"),
        ('pork -"chili peppers"', "all"),
        ("salt", "all"),
        ("chi", "all"),
        ("lettce", "all"),
        ("pork lettuce wrap", "any"),
        ("-cilantro", "all"),
    ]

    def request(entry: tuple[str, str]) -> dict:
        worker = TestClient(app)
        try:
            started = time.perf_counter()
            result = worker.get(
                "/api/recipes", headers=headers, params={"search": entry[0], "searchMode": entry[1], "perPage": 20}
            )
            elapsed = (time.perf_counter() - started) * 1000
            result.raise_for_status()
            body = result.json()
            return {
                "query": entry[0],
                "mode": entry[1],
                "ms": round(elapsed, 3),
                "total": body["total"],
                "first": body["items"][0]["name"] if body["items"] else None,
            }
        finally:
            worker.close()

    first_requests = [request(entry) for entry in corpus]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.clients) as pool:
        results = list(pool.map(request, corpus * args.repeats))
    per_query = []
    for query, mode in corpus:
        values = sorted(result["ms"] for result in results if result["query"] == query and result["mode"] == mode)
        per_query.append(
            {
                "query": query,
                "mode": mode,
                "median_ms": statistics.median(values),
                "p95_ms": values[max(0, math.ceil(len(values) * 0.95) - 1)],
            }
        )
    ordered = sorted(result["ms"] for result in results)
    report = {
        "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip(),
        "source": str(source),
        "database": engine.dialect.name,
        "database_version": str(engine.dialect.server_version_info),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python": platform.python_version(),
        "recipes": recipes,
        "ingredients_per_recipe": 8,
        "clients": args.clients,
        "requests": len(results),
        "cache": "one warmup per query; OS/database caches remain enabled",
        "transport": "in-process FastAPI TestClient; full handler/auth/serialization; excludes network/TLS",
        "semantics": (
            "Original implementation ignores searchMode and does not implement signed-term requirements/exclusions"
        ),
        "median_ms": statistics.median(ordered),
        "p95_ms": ordered[max(0, math.ceil(len(ordered) * 0.95) - 1)],
        "first_requests": first_requests,
        "queries": per_query,
        "samples": results,
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    sys.stdout.write(json.dumps({key: value for key, value in report.items() if key != "samples"}, indent=2) + "\n")


if __name__ == "__main__":
    main()
