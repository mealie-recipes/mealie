"""Client for the Recipal API.

Docs: https://www.recipal.com/api-docs
Authentication: ``Authorization: Token token=YOUR_API_KEY`` header.

All ingredient nutrition data is stored per 100 grams.
The API exposes only the user's own ingredients — there is no public
food-name search endpoint.
"""

from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)

RECIPAL_BASE_URL = "https://recipal.com/api/v1"
_TIMEOUT = 10  # seconds


class RecipalIngredient:
    """Lightweight representation of a Recipal ingredient list entry."""

    def __init__(
        self,
        ingredient_id: int,
        name: str,
        brand: str | None = None,
        usda_verified: bool = False,
    ) -> None:
        self.ingredient_id = ingredient_id
        self.name = name
        self.brand = brand
        self.usda_verified = usda_verified


class RecipalNutrition:
    """Nutrition values per 100g from Recipal, mapped to Mealie field names."""

    def __init__(self, **kwargs: float | None) -> None:
        self.calories: float | None = kwargs.get("calories")
        self.protein_content: float | None = kwargs.get("protein_content")
        self.fat_content: float | None = kwargs.get("fat_content")
        self.carbohydrate_content: float | None = kwargs.get("carbohydrate_content")
        self.fiber_content: float | None = kwargs.get("fiber_content")
        self.sugar_content: float | None = kwargs.get("sugar_content")
        self.sodium_content: float | None = kwargs.get("sodium_content")
        self.saturated_fat_content: float | None = kwargs.get("saturated_fat_content")
        self.cholesterol_content: float | None = kwargs.get("cholesterol_content")
        self.trans_fat_content: float | None = kwargs.get("trans_fat_content")
        self.unsaturated_fat_content: float | None = kwargs.get("unsaturated_fat_content")


def _auth_header(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Token token={api_key}"}


def _parse_nutrition(ing: dict) -> RecipalNutrition:
    """Map a Recipal ingredient JSON object to Mealie nutrition field names."""
    mono = ing.get("fat_monounsaturated")
    poly = ing.get("fat_polyunsaturated")
    unsaturated: float | None = None
    if mono is not None or poly is not None:
        unsaturated = (mono or 0.0) + (poly or 0.0)

    return RecipalNutrition(
        calories=ing.get("calories"),
        protein_content=ing.get("protein"),
        fat_content=ing.get("fat"),
        carbohydrate_content=ing.get("carbohydrate"),
        fiber_content=ing.get("fiber"),
        sugar_content=ing.get("sugar"),
        sodium_content=ing.get("sodium"),
        saturated_fat_content=ing.get("fat_saturated"),
        cholesterol_content=ing.get("cholesterol"),
        trans_fat_content=ing.get("fat_trans"),
        unsaturated_fat_content=unsaturated,
    )


def list_ingredients(
    api_key: str,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[RecipalIngredient], bool]:
    """List the authenticated user's Recipal ingredients (paginated, sorted by name).

    Returns ``(ingredients, has_more)`` where *has_more* is True when
    ``len(ingredients) == per_page`` (more pages may exist).
    """
    params = {
        "page": page,
        "per_page": min(per_page, 20),  # API max is 20
        "sort_field": "name",
        "sort_order": "asc",
    }
    try:
        resp = requests.get(
            f"{RECIPAL_BASE_URL}/ingredients",
            headers=_auth_header(api_key),
            params=params,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Recipal list request failed: %s", exc)
        raise RuntimeError(f"Recipal request failed: {exc}") from exc

    raw = resp.json()
    ingredients: list[RecipalIngredient] = []
    for item in raw:
        # Each item is either {"ingredient": {...}} or a bare dict
        ing = item.get("ingredient", item) if isinstance(item, dict) else {}
        ingredient_id = ing.get("id")
        name = ing.get("name") or ""
        if not ingredient_id or not name:
            continue
        ingredients.append(
            RecipalIngredient(
                ingredient_id=int(ingredient_id),
                name=name,
                brand=ing.get("brand"),
                usda_verified=bool(ing.get("usda_verified", False)),
            )
        )

    has_more = len(ingredients) == per_page
    return ingredients, has_more


def fetch_ingredient(ingredient_id: int, api_key: str) -> tuple[RecipalIngredient, RecipalNutrition]:
    """Fetch a specific Recipal ingredient by ID.

    Returns ``(ingredient_meta, nutrition)``.  Raises ``RuntimeError`` on any
    network or API error.
    """
    try:
        resp = requests.get(
            f"{RECIPAL_BASE_URL}/ingredients/{ingredient_id}",
            headers=_auth_header(api_key),
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Recipal fetch request failed for id=%s: %s", ingredient_id, exc)
        raise RuntimeError(f"Recipal request failed: {exc}") from exc

    data = resp.json()
    ing = data.get("ingredient", data)

    meta = RecipalIngredient(
        ingredient_id=int(ing["id"]),
        name=ing.get("name") or "",
        brand=ing.get("brand"),
        usda_verified=bool(ing.get("usda_verified", False)),
    )
    return meta, _parse_nutrition(ing)
