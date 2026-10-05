import json
from typing import Any


def parse_mealie_export(data: str) -> dict[str, Any] | None:
    """Return the parsed recipe when `data` is a complete recipe dump produced by Mealie, else None.

    Deliberately strict, so schema.org JSON and loose hand-written JSON keep going through the
    web scraper: only a dump carrying a slug, a group id and ingredient objects with reference
    ids qualifies. Both key styles qualify, snake_case from an export zip and camelCase from the
    API and the recipe page's JSON editor.
    """
    try:
        recipe = json.loads(data)
    except ValueError:
        return None

    if not isinstance(recipe, dict) or "@context" in recipe or "@type" in recipe:
        return None

    slug = recipe.get("slug")
    if not isinstance(slug, str) or not slug.strip():
        return None

    if "groupId" not in recipe and "group_id" not in recipe:
        return None

    ingredients = recipe.get("recipeIngredient", recipe.get("recipe_ingredient"))
    if not isinstance(ingredients, list):
        return None

    if not any(isinstance(i, dict) and ("referenceId" in i or "reference_id" in i) for i in ingredients):
        return None

    return recipe
