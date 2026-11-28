"""Measure complete search requests against a dedicated benchmark database."""

import argparse
import concurrent.futures
import json
import logging
import math
import os
import platform
import statistics
import sys
import time
from pathlib import Path
from uuid import UUID, uuid5

import sqlalchemy as sa
from fastapi.testclient import TestClient


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipes", type=int, default=10_000)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--clients", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not os.environ.get("DATA_DIR") or "search-bench" not in os.environ["DATA_DIR"]:
        parser.error("Use a dedicated DATA_DIR whose path contains search-bench")
    if os.environ.get("DB_ENGINE") == "postgres" and "bench" not in os.environ.get("POSTGRES_DB", ""):
        parser.error("Use a dedicated POSTGRES_DB whose name contains bench")

    from mealie.app import app
    from mealie.core.config import get_app_settings
    from mealie.db.db_setup import SessionLocal, engine
    from mealie.db.init_db import main as init_db
    from mealie.db.models.recipe.ingredient import RecipeIngredientModel
    from mealie.db.models.recipe.recipe import RecipeModel
    from mealie.db.models.recipe.settings import RecipeSettings
    from mealie.db.models.users.users import User
    from mealie.repos.all_repositories import get_repositories
    from mealie.schema.recipe.recipe import RecipeDraft
    from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
    from mealie.search.index import rebuild

    logging.disable(logging.CRITICAL)
    init_db()
    settings = get_app_settings()
    with SessionLocal() as session:
        user = session.scalar(sa.select(User).where(User.email == settings._DEFAULT_EMAIL))
        assert user is not None
        count = session.scalar(sa.select(sa.func.count()).select_from(RecipeModel))
        if count not in (0, 1, args.recipes):
            raise RuntimeError(f"Benchmark database has {count} recipes; use a new database")
        seed_start = time.perf_counter()
        if count != args.recipes:
            repo = get_repositories(session, group_id=user.group_id, household_id=user.household_id)
            seed = (
                repo.recipes.get_all()[0]
                if count
                else repo.recipes.create(
                    RecipeDraft(
                        name="Sesame-Lime Lettuce Cups with Pork, Red Chili Peppers & Cilantro",
                        user_id=user.id,
                        group_id=user.group_id,
                        description="Fresh lettuce cups with sesame lime sauce and spicy ground pork.",
                        recipe_ingredient=[
                            RecipeIngredient(note=note)
                            for note in (
                                "1 head butter lettuce",
                                "1 pound ground pork",
                                "2 tablespoons sesame oil",
                                "2 cloves garlic",
                                "1 lime",
                                "1 bunch cilantro",
                                "1 teaspoon salt",
                                "2 red chili peppers",
                            )
                        ],
                    )
                )
            )
            recipe_table = RecipeModel.__table__
            ingredient_table = RecipeIngredientModel.__table__
            settings_table = RecipeSettings.__table__
            recipe_template = dict(
                session.execute(sa.select(recipe_table).where(recipe_table.c.id == seed.id)).mappings().one()
            )
            ingredient_templates = [
                dict(row)
                for row in session.execute(
                    sa.select(ingredient_table).where(ingredient_table.c.recipe_id == seed.id)
                ).mappings()
            ]
            settings_template = dict(
                session.execute(sa.select(settings_table).where(settings_table.c.recipe_id == seed.id)).mappings().one()
            )
            namespace = UUID("77af5b78-7502-4c37-ae59-2f8a78403344")
            titles = (
                "Roast Chicken with Garlic and Lemon",
                "Pork Chops with Apple Slaw",
                "Chicken Lettuce Cups",
                "Crispy Tofu Rice Bowl",
                "Beef Lettuce Wraps",
                "Creamy Tomato Pasta",
                "Salmon with Herbs",
                "Black Bean Tacos",
                "Sesame Pork Lettuce Cups",
                "Chickpea Spinach Curry",
            )
            for start in range(1, args.recipes, 250):
                recipes, ingredients, preferences = [], [], []
                for number in range(start, min(start + 250, args.recipes)):
                    recipe_id = UUID(hex=uuid5(namespace, f"recipe-{number}").hex, version=4)
                    title = titles[number % len(titles)]
                    recipes.append(
                        recipe_template
                        | {
                            "id": recipe_id,
                            "name": f"{title} {number}",
                            "name_normalized": f"{title.lower()} {number}",
                            "slug": f"search-benchmark-{number}",
                            "description": (
                                f"A weeknight meal: {title}. Serve with fresh vegetables and a bright citrus sauce."
                            ),
                            "description_normalized": f"a weeknight meal {title.lower()}",
                        }
                    )
                    preferences.append(settings_template | {"id": number + 1, "recipe_id": recipe_id})
                    protein = title.split()[0].lower()
                    for position, template in enumerate(ingredient_templates):
                        note = f"1 pound {protein}" if position == 1 else template["note"]
                        if position == 0 and "Lettuce" not in title:
                            note = "2 cups seasonal vegetables"
                        ingredients.append(
                            template
                            | {
                                "id": number * len(ingredient_templates) + position + 1,
                                "recipe_id": recipe_id,
                                "reference_id": UUID(
                                    hex=uuid5(namespace, f"reference-{number}-{position}").hex, version=4
                                ),
                                "note": note,
                                "note_normalized": note.lower(),
                            }
                        )
                session.execute(recipe_table.insert(), recipes)
                session.execute(settings_table.insert(), preferences)
                session.execute(ingredient_table.insert(), ingredients)
                session.commit()
        seed_seconds = time.perf_counter() - seed_start
        rebuild_start = time.perf_counter()
        rebuild(session.connection())
        session.commit()
        rebuild_seconds = time.perf_counter() - rebuild_start
        source_write_ms = []
        benchmark_id = session.scalar(sa.select(RecipeModel.id).limit(1))
        for _ in range(20):
            write_start = time.perf_counter()
            session.execute(
                sa.update(RecipeModel).where(RecipeModel.id == benchmark_id).values(description=RecipeModel.description)
            )
            session.commit()
            source_write_ms.append((time.perf_counter() - write_start) * 1000)
        if engine.dialect.name == "postgresql":
            session.execute(sa.text("ANALYZE"))
            index_bytes = session.scalar(
                sa.text(
                    "SELECT sum(pg_total_relation_size(oid)) FROM pg_class "
                    "WHERE relkind='r' AND relname LIKE 'recipe_search_%'"
                )
            )
        else:
            session.execute(sa.text("ANALYZE"))
            index_bytes = session.scalar(
                sa.text(
                    "SELECT sum(pgsize) FROM dbstat WHERE name LIKE 'recipe_search_%' "
                    "OR name LIKE 'ix_recipe_search_%' OR name LIKE 'sqlite_autoindex_recipe_search_%'"
                )
            )
        session.commit()

    client = TestClient(app)
    response = client.post(
        "/api/auth/token", data={"username": settings._DEFAULT_EMAIL, "password": settings._DEFAULT_PASSWORD}
    )
    response.raise_for_status()
    headers = {"Authorization": "Bearer " + response.json()["access_token"]}
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

    first_requests = []
    for entry in corpus:
        result = request(entry)
        first_requests.append(result)
        sys.stdout.write(f"Warmup {entry!r}: {result['ms']:.3f} ms\n")
        sys.stdout.flush()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.clients) as pool:
        results = []
        for number, result in enumerate(pool.map(request, corpus * args.repeats), start=1):
            results.append(result)
            if number % 100 == 0:
                sys.stdout.write(f"Completed {number}/{len(corpus) * args.repeats} requests\n")
                sys.stdout.flush()
    per_query = []
    for query, mode in corpus:
        values = [result["ms"] for result in results if result["query"] == query and result["mode"] == mode]
        per_query.append(
            {
                "query": query,
                "mode": mode,
                "median_ms": statistics.median(values),
                "p95_ms": sorted(values)[max(0, math.ceil(len(values) * 0.95) - 1)],
            }
        )
    ordered = sorted(result["ms"] for result in results)
    report = {
        "database": engine.dialect.name,
        "database_version": str(engine.dialect.server_version_info),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python": platform.python_version(),
        "recipes": args.recipes,
        "ingredients_per_recipe": 8,
        "clients": args.clients,
        "requests": len(results),
        "cache": "one warmup per query; OS/database caches remain enabled",
        "transport": (
            "in-process FastAPI TestClient; includes full HTTP handler, auth, serialization; excludes network/TLS"
        ),
        "seed_seconds": seed_seconds,
        "rebuild_seconds": rebuild_seconds,
        "search_storage_bytes": int(index_bytes or 0),
        "source_update_commit_median_ms": statistics.median(source_write_ms),
        "source_update_commit_p95_ms": sorted(source_write_ms)[18],
        "median_ms": statistics.median(ordered),
        "p95_ms": ordered[max(0, math.ceil(len(ordered) * 0.95) - 1)],
        "target_p95_ms": 200,
        "passes_target": ordered[max(0, math.ceil(len(ordered) * 0.95) - 1)] <= 200,
        "first_requests": first_requests,
        "queries": per_query,
        "samples": results,
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    sys.stdout.write(
        json.dumps({key: value for key, value in report.items() if key not in ("samples", "first_requests")}, indent=2)
        + "\n"
    )


if __name__ == "__main__":
    main()
