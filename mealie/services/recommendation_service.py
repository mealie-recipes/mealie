from __future__ import annotations

import logging
import os
from collections.abc import Iterable
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from mealie.db.db_setup import session_context
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.users.user_ml_preferences import UserMLPreferences

log = logging.getLogger(__name__)

INFERENCE_URL = os.getenv("INFERENCE_API_URL", "http://inference-api:8000")
LEARNING_RATE = 0.1
COLD_START_THRESHOLD = 5
REQUEST_TIMEOUT = 2.0
RATING_WEIGHTS: dict[int, float] = {5: 1.0, 4: 0.7, 3: 0.0, 2: -0.5, 1: -1.0}


def get_prefs(db: Session, user_id: Any) -> UserMLPreferences | None:
    return db.execute(select(UserMLPreferences).filter(UserMLPreferences.user_id == user_id)).scalar_one_or_none()


def get_or_create_prefs(db: Session, user_id: Any) -> UserMLPreferences:
    prefs = get_prefs(db, user_id)
    if prefs is None:
        prefs = UserMLPreferences(user_id=user_id, rating_count=0)
        db.add(prefs)
        db.flush()
    return prefs


def _clean_tags(tags: Iterable[str]) -> list[str]:
    cleaned = [tag.strip() for tag in tags if isinstance(tag, str) and tag.strip()]
    return list(dict.fromkeys(cleaned))


def _normalize_vector(vector: Any) -> list[float] | None:
    if not isinstance(vector, list) or not vector:
        return None

    normalized: list[float] = []
    for value in vector:
        try:
            normalized.append(float(value))
        except (TypeError, ValueError):
            return None

    return normalized if any(abs(value) > 1e-8 for value in normalized) else None


def fetch_tag_vector(tags: Iterable[str]) -> list[float] | None:
    cleaned_tags = _clean_tags(tags)
    if not cleaned_tags:
        return None

    try:
        response = httpx.post(
            f"{INFERENCE_URL}/tag-vector",
            json={"tags": cleaned_tags},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except Exception as exc:
        log.warning("tag-vector request failed: %s", exc)
        return None

    return _normalize_vector(response.json().get("vector"))


def _serialize_recipe(recipe: RecipeModel) -> dict[str, Any]:
    return {
        "recipe_id": str(recipe.id),
        "slug": recipe.slug,
        "name": recipe.name,
        "description": recipe.description,
        "image": recipe.image,
        "rating": recipe.rating,
        "tags": [tag.name for tag in recipe.tags],
    }


def _baseline_recommendations(library_recipes: list[dict[str, Any]], top_n: int = 10) -> list[dict[str, Any]]:
    ranked = sorted(
        library_recipes,
        key=lambda recipe: (
            -(recipe.get("rating") or 0.0),
            (recipe.get("name") or "").lower(),
        ),
    )

    results: list[dict[str, Any]] = []
    for index, recipe in enumerate(ranked[:top_n], start=1):
        results.append(
            {
                **recipe,
                "rank": index,
                "score": recipe.get("rating"),
                "because_tags": recipe.get("tags", [])[:3],
            }
        )
    return results


async def fetch_recommendations(
    db: Session,
    user_id: Any,
    recipes: list[RecipeModel],
    *,
    top_n: int = 10,
) -> dict[str, Any]:
    library_recipes = [_serialize_recipe(recipe) for recipe in recipes]
    if not library_recipes:
        return {
            "recommendations": [],
            "cold_start": True,
            "model_version": "empty_library",
        }

    prefs = get_prefs(db, user_id)
    is_cold = (prefs.rating_count if prefs else 0) < COLD_START_THRESHOLD
    taste_vector = _normalize_vector(prefs.taste_vector if prefs else None)
    if taste_vector is None:
        return {
            "recommendations": _baseline_recommendations(library_recipes, top_n),
            "cold_start": True,
            "model_version": "popularity_baseline",
        }

    recipe_lookup = {recipe["recipe_id"]: recipe for recipe in library_recipes}
    payload = {
        "user_id": str(user_id),
        "user_vector": taste_vector,
        "library_recipes": [
            {
                "recipe_id": recipe["recipe_id"],
                "name": recipe["name"],
                "tags": recipe["tags"],
            }
            for recipe in library_recipes
        ],
        "top_n": top_n,
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(f"{INFERENCE_URL}/recommend", json=payload)
            response.raise_for_status()
        data = response.json()
    except Exception as exc:
        log.error("recommendation fetch failed for %s: %s", user_id, exc)
        return {
            "recommendations": _baseline_recommendations(library_recipes, top_n),
            "cold_start": is_cold,
            "model_version": "fallback",
        }

    enriched: list[dict[str, Any]] = []
    for index, recommendation in enumerate(data.get("recommendations", []), start=1):
        recipe_id = str(recommendation.get("recipe_id") or "")
        recipe = recipe_lookup.get(recipe_id)
        if recipe is None:
            continue

        because_tags = recommendation.get("because_tags") or recipe.get("tags", [])[:3]
        enriched.append(
            {
                **recipe,
                "rank": recommendation.get("rank", index),
                "score": recommendation.get("score"),
                "because_tags": because_tags[:3],
            }
        )

    if not enriched:
        enriched = _baseline_recommendations(library_recipes, top_n)

    return {
        "recommendations": enriched[:top_n],
        "cold_start": is_cold,
        "model_version": data.get("model_version", "inference-api"),
    }


def update_vector_on_rating(user_id: Any, recipe_tags: Iterable[str], star_rating: int) -> None:
    weight = RATING_WEIGHTS.get(int(star_rating), 0.0)
    cleaned_tags = _clean_tags(recipe_tags)

    with session_context() as db:
        prefs = get_or_create_prefs(db, user_id)
        prefs.rating_count = (prefs.rating_count or 0) + 1

        user_vector = _normalize_vector(prefs.taste_vector)
        if weight == 0.0 or user_vector is None or not cleaned_tags:
            db.commit()
            return

        recipe_vector = fetch_tag_vector(cleaned_tags)
        if recipe_vector is None:
            db.commit()
            return

        if len(user_vector) != len(recipe_vector):
            prefs.taste_vector = recipe_vector
            db.commit()
            return

        prefs.taste_vector = [
            round(user_value + (LEARNING_RATE * weight * recipe_value), 6)
            for user_value, recipe_value in zip(user_vector, recipe_vector)
        ]
        db.commit()
