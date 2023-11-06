from pydantic import UUID4

from mealie.core.config import get_app_settings


def _base_or(base_url: str | None) -> str:
    if base_url is None:
        settings = get_app_settings()
        return settings.BASE_URL

    return base_url


def recipe_url(group_slug: str, recipe_slug: str, base_url: str | None) -> str:
    base = _base_or(base_url)
    return f"{base}/g/{group_slug}/r/{recipe_slug}"


def shopping_list_url(shopping_list_id: UUID4 | str, base_url: str | None) -> str:
    base = _base_or(base_url)
    return f"{base}/shopping-list/{shopping_list_id}"


def tag_url(tag_slug: str, base_url: str | None) -> str:
    base = _base_or(base_url)
    return f"{base}/recipes/tags/{tag_slug}"


def category_url(category_slug: str, base_url: str | None) -> str:
    base = _base_or(base_url)
    return f"{base}/recipes/categories/{category_slug}"


def tool_url(tool_slug: str, base_url: str | None) -> str:
    base = _base_or(base_url)
    return f"{base}/recipes/tool/{tool_slug}"
