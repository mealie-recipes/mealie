from typing import Dict, Iterable, List, MutableMapping, Optional

import numpy as np

DEFAULT_VECTOR_DIM = 50
CUISINE_TAGS = {
    "italian", "asian", "mexican", "indian", "greek",
    "french", "chinese", "thai", "spanish", "american",
}


def _resolve_vector_dim(
    tag_to_vector: Dict[str, np.ndarray],
    vector_dim: Optional[int],
) -> int:
    if vector_dim is not None:
        return int(vector_dim)
    if tag_to_vector:
        first_vector = next(iter(tag_to_vector.values()))
        return int(np.asarray(first_vector).shape[0])
    return DEFAULT_VECTOR_DIM


def get_recipe_vector(
    tags: Iterable[str],
    tag_to_vector: Dict[str, np.ndarray],
    vector_dim: Optional[int] = None,
) -> np.ndarray:
    resolved_dim = _resolve_vector_dim(tag_to_vector, vector_dim)
    vecs = [tag_to_vector[tag] for tag in tags if tag in tag_to_vector]
    if not vecs:
        return np.zeros(resolved_dim, dtype=np.float32)
    return np.mean(np.stack(vecs), axis=0).astype(np.float32)


def precompute_recipe_cache(
    library_recipes: List[Dict],
    tag_to_vector: Dict[str, np.ndarray],
    vector_dim: Optional[int] = None,
) -> Dict[str, np.ndarray]:
    cache: Dict[str, np.ndarray] = {}
    resolved_dim = _resolve_vector_dim(tag_to_vector, vector_dim)
    for recipe in library_recipes:
        recipe_id = recipe.get("recipe_id")
        if recipe_id:
            cache[recipe_id] = get_recipe_vector(
                recipe.get("tags", []),
                tag_to_vector,
                vector_dim=resolved_dim,
            )
    return cache


def apply_diversity(
    ranked: List[Dict],
    *,
    limit: Optional[int] = None,
    max_per_cuisine: int = 3,
) -> List[Dict]:
    counts: Dict[str, int] = {}
    kept: List[Dict] = []
    rest: List[Dict] = []

    for recipe in ranked:
        cuisine = next((tag for tag in recipe.get("tags", []) if tag in CUISINE_TAGS), None)
        if cuisine and counts.get(cuisine, 0) >= max_per_cuisine:
            rest.append(recipe)
            continue

        if cuisine:
            counts[cuisine] = counts.get(cuisine, 0) + 1
        kept.append(recipe)

    diversified = kept + rest
    return diversified[:limit] if limit is not None else diversified


def rank_recipes(
    user_vector: np.ndarray,
    library_recipes: List[Dict],
    tag_to_vector: Dict[str, np.ndarray],
    top_n: int = 10,
    recipe_cache: Optional[MutableMapping[str, np.ndarray]] = None,
) -> List[Dict]:
    scored: List[Dict] = []
    vector_dim = int(user_vector.shape[0]) if user_vector.ndim else DEFAULT_VECTOR_DIM

    for recipe in library_recipes:
        recipe_id = recipe.get("recipe_id")
        recipe_vector = None

        if recipe_cache is not None and recipe_id:
            recipe_vector = recipe_cache.get(recipe_id)

        if recipe_vector is None:
            recipe_vector = get_recipe_vector(
                recipe.get("tags", []),
                tag_to_vector,
                vector_dim=vector_dim,
            )
            if recipe_cache is not None and recipe_id:
                recipe_cache[recipe_id] = recipe_vector

        matched = [tag for tag in recipe.get("tags", []) if tag in tag_to_vector]
        score = float(np.dot(user_vector, recipe_vector))
        scored.append(
            {
                "recipe_id": recipe.get("recipe_id"),
                "name": recipe.get("name"),
                "tags": recipe.get("tags", []),
                "score": round(score, 4),
                "because_tags": matched[:3],
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    diversified = apply_diversity(
        scored[: max(top_n * 2, 20)],
        limit=top_n,
    )
    return [{"rank": idx + 1, **recipe} for idx, recipe in enumerate(diversified)]
