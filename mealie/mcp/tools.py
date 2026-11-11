"""Curated task-oriented Mealie tools, each scoped to the authenticated household."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from typing import Any
from uuid import UUID

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.types import ToolAnnotations
from pydantic import BaseModel, ConfigDict

from mealie.db.db_setup import session_context
from mealie.db.models.users.users import User
from mealie.lang.providers import get_locale_provider
from mealie.mcp.server import mcp
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.group_shopping_list import (
    ShoppingListCreate,
    ShoppingListItemCreate,
    ShoppingListItemUpdateBulk,
    ShoppingListOut,
)
from mealie.schema.household.household import HouseholdOut
from mealie.schema.meal_plan.new_meal import PlanEntrySave, PlanEntryType
from mealie.schema.recipe.recipe import RecipeCreate, RecipeDraft, RecipeSummary
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.user import PrivateUser
from mealie.services.household_services.shopping_lists import ShoppingListService
from mealie.services.recipe.recipe_service import RecipeService

TOOL_SCOPES = {
    "get_profile": "profile:read",
    "search_recipes": "recipes:read",
    "get_recipe": "recipes:read",
    "create_recipe": "recipes:write",
    "update_recipe": "recipes:write",
    "list_meal_plan": "mealplans:read",
    "add_meal_plan_entry": "mealplans:write",
    "update_meal_plan_entry": "mealplans:write",
    "list_shopping_lists": "shopping:read",
    "get_shopping_list": "shopping:read",
    "add_shopping_item": "shopping:write",
    "update_shopping_item": "shopping:write",
    "set_shopping_item_checked": "shopping:write",
    "delete_shopping_item": "shopping:write",
    "set_all_shopping_items_checked": "shopping:write",
    "clear_checked_shopping_items": "shopping:write",
    "create_shopping_list": "shopping:write",
    "rename_shopping_list": "shopping:write",
}

READ = ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=False)
WRITE = ToolAnnotations(read_only_hint=False, destructive_hint=False, open_world_hint=False)
UPDATE = ToolAnnotations(read_only_hint=False, destructive_hint=True, open_world_hint=False)
logger = logging.getLogger("mealie.mcp")


class McpProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str | None = None
    email: str | None = None
    nickname: str | None = None


def _tool_meta(name: str) -> dict[str, Any]:
    meta: dict[str, Any] = {"securitySchemes": [{"type": "oauth2", "scopes": [TOOL_SCOPES[name]]}]}
    if name == "get_profile":
        meta["openai/profile"] = True
    return meta


@contextmanager
def _context(required_scope: str) -> Iterator[tuple[PrivateUser, AllRepositories, HouseholdOut]]:
    token = get_access_token()
    if not token or required_scope not in token.scopes or not token.subject:
        raise PermissionError(f"Missing required MCP scope: {required_scope}")
    with session_context() as session:
        user_model = session.get(User, UUID(token.subject))
        if not user_model or str(user_model.household_id) != (token.claims or {}).get("household_id"):
            raise PermissionError("Mealie household access has changed")
        user = PrivateUser.model_validate(user_model)
        repos = get_repositories(session, group_id=user.group_id, household_id=user.household_id)
        household = repos.households.get_one(user.household_id)
        if household is None:
            raise PermissionError("Mealie household is unavailable")
        yield user, repos, household


def _page(page: int, per_page: int) -> PaginationQuery:
    if page < 1 or not 1 <= per_page <= 100:
        raise ValueError("page must be positive and per_page must be between 1 and 100")
    return PaginationQuery(page=page, per_page=per_page)


def _is_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except ValueError:
        return False


def _summary(item, url: str | None = None) -> dict:
    result = item.model_dump(mode="json", by_alias=True)
    if url:
        result["url"] = url
    return result


@mcp.tool(
    description="Identify the connected Mealie account and household.", annotations=READ, meta=_tool_meta("get_profile")
)
def get_profile() -> McpProfile:
    with _context("profile:read") as (user, _, __):
        return McpProfile(id=str(user.id), name=user.full_name, email=user.email, nickname=user.household)


@mcp.tool(description="Search recipes in the connected household.", annotations=READ, meta=_tool_meta("search_recipes"))
def search_recipes(search: str = "", page: int = 1, per_page: int = 25) -> dict:
    from mealie.mcp.oauth import public_base_url

    with _context("recipes:read") as (user, repos, _):
        found = repos.recipes.by_user(user.id).page_all(
            _page(page, per_page), override=RecipeSummary, search=search or None
        )
        return {
            "page": found.page,
            "total": found.total,
            "items": [
                _summary(recipe, f"{public_base_url()}/g/{user.group_slug}/r/{recipe.slug}") for recipe in found.items
            ],
        }


@mcp.tool(
    description="Read a recipe by its slug or ID in the connected household.",
    annotations=READ,
    meta=_tool_meta("get_recipe"),
)
def get_recipe(slug_or_id: str) -> dict:
    from mealie.mcp.oauth import public_base_url

    with _context("recipes:read") as (user, repos, household):
        if not (
            repos.recipes.get_one(slug_or_id, "id")
            if _is_uuid(slug_or_id)
            else repos.recipes.get_one(slug_or_id, "slug")
        ):
            raise ValueError("Recipe not found in this household")
        recipe = RecipeService(repos, user, household, get_locale_provider("en-US")).get_one(slug_or_id)
        return _summary(recipe, f"{public_base_url()}/g/{user.group_slug}/r/{recipe.slug}")


@mcp.tool(
    description="Create a new recipe in the connected household.", annotations=WRITE, meta=_tool_meta("create_recipe")
)
def create_recipe(name: str) -> dict:
    from mealie.mcp.oauth import public_base_url

    if not name.strip() or len(name) > 250:
        raise ValueError("Recipe name must be 1 to 250 characters")
    with _context("recipes:write") as (user, repos, household):
        recipe = RecipeService(repos, user, household, get_locale_provider("en-US")).create_one(
            RecipeCreate(name=name.strip())
        )
        logger.info("MCP create_recipe by user %s", user.id)
        return {
            "id": str(recipe.id),
            "slug": recipe.slug,
            "name": recipe.name,
            "url": f"{public_base_url()}/g/{user.group_slug}/r/{recipe.slug}",
        }


@mcp.tool(
    description="Change a recipe's name or description where the connected user may edit it.",
    annotations=UPDATE,
    meta=_tool_meta("update_recipe"),
)
def update_recipe(slug_or_id: str, name: str | None = None, description: str | None = None) -> dict:
    if name is None and description is None:
        raise ValueError("Provide a name or description")
    if name is not None and (not name.strip() or len(name) > 250):
        raise ValueError("Recipe name must be 1 to 250 characters")
    with _context("recipes:write") as (user, repos, household):
        service = RecipeService(repos, user, household, get_locale_provider("en-US"))
        existing = service.get_one(slug_or_id)
        if not repos.recipes.get_one(existing.id, "id"):
            raise ValueError("Recipe not found in this household")
        changes: dict[str, object] = {}
        if name is not None:
            changes["name"] = name.strip()
        if description is not None:
            changes["description"] = description
        updated = service.update_one(existing.slug, RecipeDraft.model_validate({**existing.model_dump(), **changes}))
        logger.info("MCP update_recipe by user %s", user.id)
        return {"id": str(updated.id), "slug": updated.slug, "name": updated.name}


@mcp.tool(
    description="List meal plan entries for the connected household.",
    annotations=READ,
    meta=_tool_meta("list_meal_plan"),
)
def list_meal_plan(
    page: int = 1, per_page: int = 25, start_date: date | None = None, end_date: date | None = None
) -> dict:
    with _context("mealplans:read") as (_, repos, __):
        q = _page(page, per_page)
        filters = []
        if start_date:
            filters.append(f"date >= {start_date.isoformat()}")
        if end_date:
            filters.append(f"date <= {end_date.isoformat()}")
        if filters:
            q.query_filter = " AND ".join(filters)
        found = repos.meals.page_all(q)
        return {"page": found.page, "total": found.total, "items": [_summary(item) for item in found.items]}


@mcp.tool(
    description="Add a meal plan entry for the connected household.",
    annotations=WRITE,
    meta=_tool_meta("add_meal_plan_entry"),
)
def add_meal_plan_entry(
    date: date, title: str = "", recipe_id: str | None = None, entry_type: PlanEntryType = PlanEntryType.dinner
) -> dict:
    if not title and not recipe_id:
        raise ValueError("Provide a title or recipe_id")
    with _context("mealplans:write") as (user, repos, _):
        recipe_uuid = UUID(recipe_id) if recipe_id else None
        if recipe_uuid and not repos.recipes.get_one(recipe_uuid, "id"):
            raise ValueError("Recipe not found in this household")
        item = repos.meals.create(
            PlanEntrySave(
                date=date,
                title=title,
                recipe_id=recipe_uuid,
                entry_type=entry_type,
                group_id=user.group_id,
                user_id=user.id,
            )
        )
        logger.info("MCP add_meal_plan_entry by user %s", user.id)
        return _summary(item)


@mcp.tool(
    description="Change the title, date, or meal type of a household meal plan entry.",
    annotations=UPDATE,
    meta=_tool_meta("update_meal_plan_entry"),
)
def update_meal_plan_entry(
    entry_id: int, date: date | None = None, title: str | None = None, entry_type: PlanEntryType | None = None
) -> dict:
    with _context("mealplans:write") as (user, repos, __):
        if not repos.meals.get_one(entry_id):
            raise ValueError("Meal plan entry not found")
        changes: dict[str, object] = {}
        if date is not None:
            changes["date"] = date
        if title is not None:
            changes["title"] = title
        if entry_type is not None:
            changes["entry_type"] = entry_type
        if not changes:
            raise ValueError("Provide a change")
        result = repos.meals.patch(entry_id, changes)
        logger.info("MCP update_meal_plan_entry by user %s", user.id)
        return _summary(result)


@mcp.tool(
    description="List shopping lists in the connected household.",
    annotations=READ,
    meta=_tool_meta("list_shopping_lists"),
)
def list_shopping_lists(page: int = 1, per_page: int = 25) -> dict:
    with _context("shopping:read") as (_, repos, __):
        found = repos.group_shopping_lists.page_all(_page(page, per_page))
        return {"page": found.page, "total": found.total, "items": [_summary(item) for item in found.items]}


@mcp.tool(
    description="Read a household shopping list and its items.", annotations=READ, meta=_tool_meta("get_shopping_list")
)
def get_shopping_list(list_id: str) -> dict:
    with _context("shopping:read") as (_, repos, __):
        item = repos.group_shopping_lists.get_one(UUID(list_id))
        if not item:
            raise ValueError("Shopping list not found")
        return _summary(item)


@mcp.tool(
    description="Add an item to a household shopping list.", annotations=WRITE, meta=_tool_meta("add_shopping_item")
)
def add_shopping_item(list_id: str, note: str, quantity: float = 1) -> dict:
    with _context("shopping:write") as (user, repos, __):
        list_uuid = UUID(list_id)
        if not repos.group_shopping_lists.get_one(list_uuid):
            raise ValueError("Shopping list not found")
        if not note.strip() or quantity <= 0:
            raise ValueError("Provide an item name and positive quantity")
        result = ShoppingListService(repos).bulk_create_items(
            [ShoppingListItemCreate(shopping_list_id=list_uuid, note=note.strip(), quantity=quantity)]
        )
        logger.info("MCP add_shopping_item by user %s", user.id)
        return result.model_dump(mode="json", by_alias=True)


def _update_item(
    item_id: str, note: str | None = None, quantity: float | None = None, checked: bool | None = None
) -> dict:
    with _context("shopping:write") as (user, repos, __):
        item = repos.group_shopping_list_item.get_one(UUID(item_id))
        if not item:
            raise ValueError("Shopping item not found")
        if quantity is not None and quantity <= 0:
            raise ValueError("Quantity must be positive")
        changes = item.model_dump(mode="python")
        if note is not None:
            changes["note"] = note
        if quantity is not None:
            changes["quantity"] = quantity
        if checked is not None:
            changes["checked"] = checked
        result = ShoppingListService(repos).bulk_update_items([ShoppingListItemUpdateBulk.model_validate(changes)])
        logger.info("MCP update_shopping_item by user %s", user.id)
        return result.model_dump(mode="json", by_alias=True)


@mcp.tool(
    description="Edit an item on a household shopping list.",
    annotations=UPDATE,
    meta=_tool_meta("update_shopping_item"),
)
def update_shopping_item(item_id: str, note: str | None = None, quantity: float | None = None) -> dict:
    if note is None and quantity is None:
        raise ValueError("Provide a note or quantity")
    return _update_item(item_id, note=note, quantity=quantity)


@mcp.tool(
    description="Check or uncheck an item on a household shopping list.",
    annotations=UPDATE,
    meta=_tool_meta("set_shopping_item_checked"),
)
def set_shopping_item_checked(item_id: str, checked: bool) -> dict:
    return _update_item(item_id, checked=checked)


def _shopping_list(repos: AllRepositories, list_id: str) -> ShoppingListOut:
    found = repos.group_shopping_lists.get_one(UUID(list_id))
    if not found:
        raise ValueError("Shopping list not found")
    return found


def _list_name(name: str) -> str:
    if not name.strip() or len(name) > 250:
        raise ValueError("Shopping list name must be 1 to 250 characters")
    return name.strip()


@mcp.tool(
    description="Remove an item from a household shopping list.",
    annotations=UPDATE,
    meta=_tool_meta("delete_shopping_item"),
)
def delete_shopping_item(item_id: str) -> dict:
    with _context("shopping:write") as (user, repos, __):
        if not repos.group_shopping_list_item.get_one(UUID(item_id)):
            raise ValueError("Shopping item not found")
        result = ShoppingListService(repos).bulk_delete_items([UUID(item_id)])
        logger.info("MCP delete_shopping_item by user %s", user.id)
        return result.model_dump(mode="json", by_alias=True)


@mcp.tool(
    description=(
        "Check or uncheck every item on a household shopping list, e.g. to mark the whole list as done after shopping."
    ),
    annotations=UPDATE,
    meta=_tool_meta("set_all_shopping_items_checked"),
)
def set_all_shopping_items_checked(list_id: str, checked: bool = True) -> dict:
    with _context("shopping:write") as (user, repos, __):
        shopping_list = _shopping_list(repos, list_id)
        changes = [
            ShoppingListItemUpdateBulk.model_validate({**item.model_dump(mode="python"), "checked": checked})
            for item in shopping_list.list_items
            if item.checked != checked
        ]
        result = ShoppingListService(repos).bulk_update_items(changes)
        logger.info("MCP set_all_shopping_items_checked by user %s", user.id)
        return result.model_dump(mode="json", by_alias=True)


@mcp.tool(
    description="Delete all checked items from a household shopping list.",
    annotations=UPDATE,
    meta=_tool_meta("clear_checked_shopping_items"),
)
def clear_checked_shopping_items(list_id: str) -> dict:
    with _context("shopping:write") as (user, repos, __):
        shopping_list = _shopping_list(repos, list_id)
        checked = [item.id for item in shopping_list.list_items if item.checked]
        result = ShoppingListService(repos).bulk_delete_items(checked)
        logger.info("MCP clear_checked_shopping_items by user %s", user.id)
        return result.model_dump(mode="json", by_alias=True)


@mcp.tool(
    description="Create a new household shopping list.",
    annotations=WRITE,
    meta=_tool_meta("create_shopping_list"),
)
def create_shopping_list(name: str) -> dict:
    list_name = _list_name(name)
    with _context("shopping:write") as (user, repos, __):
        created = ShoppingListService(repos).create_one_list(ShoppingListCreate(name=list_name), user.id)
        logger.info("MCP create_shopping_list by user %s", user.id)
        return _summary(created)


@mcp.tool(
    description="Rename a household shopping list.",
    annotations=UPDATE,
    meta=_tool_meta("rename_shopping_list"),
)
def rename_shopping_list(list_id: str, name: str) -> dict:
    list_name = _list_name(name)
    with _context("shopping:write") as (user, repos, __):
        shopping_list = _shopping_list(repos, list_id)
        updated = repos.group_shopping_lists.patch(shopping_list.id, {"name": list_name})
        logger.info("MCP rename_shopping_list by user %s", user.id)
        return {"id": str(updated.id), "name": updated.name}
