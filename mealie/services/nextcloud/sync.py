"""Bidirectional sync between Mealie shopping lists and Nextcloud Tasks.

Each Mealie ShoppingList maps to a parent VTODO in a single configured Nextcloud task list.
Each ShoppingListItem maps to a child VTODO linked via RELATED-TO;RELTYPE=PARENT.
UID mapping is tracked via the extras dict on both ShoppingList and ShoppingListItem.
"""

import logging
from datetime import UTC, datetime
from typing import cast
from uuid import uuid4

from pydantic import UUID4

from mealie.core.config import get_app_settings
from mealie.core.settings.settings import AppSettings
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.group_shopping_list import (
    ShoppingListItemCreate,
    ShoppingListItemOut,
    ShoppingListItemUpdateBulk,
    ShoppingListOut,
    ShoppingListSummary,
)
from mealie.schema.response.pagination import PaginationQuery

from .caldav import NextcloudTasksService, VTodoItem

logger = logging.getLogger(__name__)

NC_UID_KEY = "nextcloud_uid"
NC_PARENT_UID_KEY = "nextcloud_parent_uid"
NC_LAST_SYNC_KEY = "nextcloud_last_sync"


def _item_to_summary(item: ShoppingListItemOut) -> str:
    """Convert a Mealie shopping list item to a human-readable VTODO summary."""
    parts: list[str] = []
    if item.quantity and item.quantity != 0:
        # Format as integer if whole number
        qty = int(item.quantity) if item.quantity == int(item.quantity) else item.quantity
        parts.append(str(qty))
    if item.unit:
        parts.append(item.unit.name or item.unit.abbreviation or "")
    if item.food:
        parts.append(item.food.name or "")
    if item.note:
        if parts:
            parts.append(f"- {item.note}")
        else:
            parts.append(item.note)
    return " ".join(p for p in parts if p).strip()


def _get_nc_uid(extras: dict | None) -> str | None:
    """Extract the Nextcloud VTODO UID from an item's extras."""
    if not extras:
        return None
    return extras.get(NC_UID_KEY)


def _create_nc_service(settings: AppSettings | None = None) -> NextcloudTasksService | None:
    """Create a NextcloudTasksService from app settings, or None if not configured."""
    if settings is None:
        settings = get_app_settings()
    if not settings.NEXTCLOUD_ENABLED:
        return None
    return NextcloudTasksService(
        url=settings.NEXTCLOUD_URL,  # type: ignore
        username=settings.NEXTCLOUD_USERNAME,  # type: ignore
        password=settings.NEXTCLOUD_PASSWORD,  # type: ignore
        task_list=settings.NEXTCLOUD_TASK_LIST,  # type: ignore
        verify_ssl=settings.NEXTCLOUD_VERIFY_SSL,
    )


class NextcloudSyncService:
    """Bidirectional sync between Mealie shopping lists and Nextcloud Tasks."""

    def __init__(self, repos: AllRepositories, settings: AppSettings | None = None) -> None:
        self.repos = repos
        self.settings = settings or get_app_settings()
        self.nc = _create_nc_service(self.settings)

    def _get_shopping_list(self, shopping_list_id: UUID4) -> ShoppingListOut | None:
        return cast(ShoppingListOut | None, self.repos.group_shopping_lists.get_one(shopping_list_id))

    def _get_all_shopping_lists(self) -> list[ShoppingListSummary]:
        result = self.repos.group_shopping_lists.page_all(
            PaginationQuery(page=1, per_page=-1),
            override=ShoppingListSummary,
        )
        return result.items

    def _update_item_extras(self, item_id: UUID4, key: str, value: str) -> None:
        """Update a single extra key on a shopping list item."""
        item = self.repos.group_shopping_list_item.get_one(item_id)
        if item is None:
            return
        extras = item.extras or {}
        extras[key] = value
        self.repos.group_shopping_list_item.update(item_id, item.cast(ShoppingListItemUpdateBulk, id=item_id, extras=extras))

    def _update_list_extras(self, list_id: UUID4, key: str, value: str) -> None:
        """Update a single extra key on a shopping list."""
        shopping_list = self._get_shopping_list(list_id)
        if shopping_list is None:
            return
        extras = shopping_list.extras or {}
        extras[key] = value
        shopping_list.extras = extras
        self.repos.group_shopping_lists.update(list_id, shopping_list)

    # ─── Push operations (Mealie → Nextcloud) ─────────────────────────

    async def push_list_created(self, shopping_list_id: UUID4) -> None:
        """Create a parent VTODO in Nextcloud for a new shopping list."""
        if not self.nc:
            return

        shopping_list = self._get_shopping_list(shopping_list_id)
        if not shopping_list:
            return

        parent_uid = str(uuid4())
        try:
            result = await self.nc.create_todo(
                summary=shopping_list.name or "Shopping List",
                uid=parent_uid,
            )
            if result:
                self._update_list_extras(shopping_list_id, NC_PARENT_UID_KEY, parent_uid)
                logger.info("Created Nextcloud parent task for list '%s'", shopping_list.name)
        except Exception:
            logger.exception("Failed to create Nextcloud parent task for list '%s'", shopping_list.name)

    async def push_list_deleted(self, shopping_list_id: UUID4) -> None:
        """Delete the parent VTODO and all child VTODOs from Nextcloud."""
        if not self.nc:
            return

        # We need to find the parent UID - but the list may already be deleted from DB.
        # Best effort: try to get the list, if gone, we can't delete from NC.
        shopping_list = self._get_shopping_list(shopping_list_id)
        if not shopping_list:
            return

        parent_uid = _get_nc_uid(shopping_list.extras) or (shopping_list.extras or {}).get(NC_PARENT_UID_KEY)
        if not parent_uid:
            return

        try:
            # Delete all children first
            todos = await self.nc.list_todos()
            for todo in todos:
                if todo.parent_uid == parent_uid:
                    await self.nc.delete_todo(todo.uid)
            # Delete parent
            await self.nc.delete_todo(parent_uid)
            logger.info("Deleted Nextcloud tasks for list '%s'", shopping_list.name)
        except Exception:
            logger.exception("Failed to delete Nextcloud tasks for list '%s'", shopping_list.name)

    async def push_items_created(self, shopping_list_id: UUID4, item_ids: list[UUID4]) -> None:
        """Push newly created items to Nextcloud as child VTODOs."""
        if not self.nc:
            return

        shopping_list = self._get_shopping_list(shopping_list_id)
        if not shopping_list:
            return

        parent_uid = (shopping_list.extras or {}).get(NC_PARENT_UID_KEY)
        if not parent_uid:
            # Create parent task first
            parent_uid = str(uuid4())
            result = await self.nc.create_todo(
                summary=shopping_list.name or "Shopping List",
                uid=parent_uid,
            )
            if result:
                self._update_list_extras(shopping_list_id, NC_PARENT_UID_KEY, parent_uid)
            else:
                logger.error("Failed to create parent task for list '%s'", shopping_list.name)
                return

        for item_id in item_ids:
            item = cast(ShoppingListItemOut | None, self.repos.group_shopping_list_item.get_one(item_id))
            if not item:
                continue

            # Skip if already synced
            nc_uid = _get_nc_uid(item.extras)
            if nc_uid:
                continue

            summary = _item_to_summary(item)
            child_uid = str(uuid4())
            try:
                status = "COMPLETED" if item.checked else "NEEDS-ACTION"
                result = await self.nc.create_todo(
                    summary=summary,
                    parent_uid=parent_uid,
                    uid=child_uid,
                    status=status,
                )
                if result:
                    self._update_item_extras(item_id, NC_UID_KEY, child_uid)
            except Exception:
                logger.exception("Failed to push item '%s' to Nextcloud", summary)

    async def push_items_updated(self, shopping_list_id: UUID4, item_ids: list[UUID4]) -> None:
        """Push item updates (including check status) to Nextcloud."""
        if not self.nc:
            return

        for item_id in item_ids:
            item = cast(ShoppingListItemOut | None, self.repos.group_shopping_list_item.get_one(item_id))
            if not item:
                continue

            nc_uid = _get_nc_uid(item.extras)
            if not nc_uid:
                # Item not yet synced — create it
                await self.push_items_created(shopping_list_id, [item_id])
                continue

            try:
                # Update summary
                summary = _item_to_summary(item)
                await self.nc.update_todo_summary(nc_uid, summary)

                # Update check status
                if item.checked:
                    await self.nc.complete_todo(nc_uid)
                else:
                    await self.nc.uncomplete_todo(nc_uid)
            except Exception:
                logger.exception("Failed to update item '%s' in Nextcloud", nc_uid)

    async def push_items_deleted(self, shopping_list_id: UUID4, item_ids: list[UUID4]) -> None:
        """Delete VTODOs from Nextcloud for removed items."""
        if not self.nc:
            return

        # Items are already deleted from DB, so we need to get nc_uids before deletion.
        # This is called after the items are deleted, so we rely on the event data.
        # We need to fetch todos from NC and match by known UIDs.
        # Since items are gone, we'll try to delete by uid from the item_ids.
        # The caller should pass nc_uids if possible, but as a fallback we try each.

        # Best approach: items still have their extras at event time in the controller
        # The event listener should capture nc_uids before items are deleted.
        # For now, we'll handle this in the event listener by pre-fetching uids.
        pass

    async def push_items_deleted_by_nc_uids(self, nc_uids: list[str]) -> None:
        """Delete VTODOs from Nextcloud by their UIDs."""
        if not self.nc:
            return

        for nc_uid in nc_uids:
            try:
                await self.nc.delete_todo(nc_uid)
            except Exception:
                logger.exception("Failed to delete VTODO '%s' from Nextcloud", nc_uid)

    # ─── Pull operations (Nextcloud → Mealie) ─────────────────────────

    async def pull_changes(self, shopping_list_id: UUID4) -> None:
        """Pull changes from Nextcloud for a specific shopping list."""
        if not self.nc:
            return

        shopping_list = self._get_shopping_list(shopping_list_id)
        if not shopping_list:
            return

        parent_uid = (shopping_list.extras or {}).get(NC_PARENT_UID_KEY)
        if not parent_uid:
            # This list hasn't been synced to Nextcloud yet; push it first
            await self.push_list_created(shopping_list_id)
            # Push existing items
            item_ids = [item.id for item in shopping_list.list_items]
            if item_ids:
                await self.push_items_created(shopping_list_id, item_ids)
            return

        try:
            todos = await self.nc.list_todos()
        except Exception:
            logger.exception("Failed to fetch Nextcloud tasks for pull")
            return

        # Find children of this parent
        nc_children = {t.uid: t for t in todos if t.parent_uid == parent_uid}

        # Build map of existing Mealie items by their NC UID
        mealie_items_by_nc_uid: dict[str, ShoppingListItemOut] = {}
        mealie_items_without_nc: list[ShoppingListItemOut] = []
        for item in shopping_list.list_items:
            nc_uid = _get_nc_uid(item.extras)
            if nc_uid:
                mealie_items_by_nc_uid[nc_uid] = item
            else:
                mealie_items_without_nc.append(item)

        # 1. Sync check status from Nextcloud → Mealie
        for nc_uid, todo in nc_children.items():
            mealie_item = mealie_items_by_nc_uid.get(nc_uid)
            if not mealie_item:
                continue

            nc_is_completed = todo.status in ("COMPLETED", "DONE")
            if nc_is_completed != mealie_item.checked:
                # Update Mealie to match Nextcloud
                self.repos.group_shopping_list_item.update(
                    mealie_item.id,
                    mealie_item.cast(ShoppingListItemUpdateBulk, id=mealie_item.id, checked=nc_is_completed),
                )
                logger.debug("Synced check status from NC for item '%s': checked=%s", todo.summary, nc_is_completed)

        # 2. Create Mealie items for NC tasks that don't exist in Mealie
        known_nc_uids = set(mealie_items_by_nc_uid.keys())
        for nc_uid, todo in nc_children.items():
            if nc_uid in known_nc_uids:
                continue
            if todo.status in ("COMPLETED", "DONE"):
                continue  # Don't import completed tasks from NC

            # Create a new item in Mealie
            new_item = ShoppingListItemCreate(
                shopping_list_id=shopping_list_id,
                note=todo.summary,
                checked=False,
                quantity=1,
                extras={NC_UID_KEY: nc_uid},
            )
            created = self.repos.group_shopping_list_item.create(new_item)
            if created:
                logger.debug("Imported item from Nextcloud: '%s'", todo.summary)

        # 3. Delete NC tasks that were deleted in Mealie (NC has it, Mealie doesn't)
        # This is handled by push_items_deleted, not during pull

        # 4. Push items that exist in Mealie but not in Nextcloud
        for item in mealie_items_without_nc:
            child_uid = str(uuid4())
            summary = _item_to_summary(item)
            status = "COMPLETED" if item.checked else "NEEDS-ACTION"
            try:
                result = await self.nc.create_todo(
                    summary=summary,
                    parent_uid=parent_uid,
                    uid=child_uid,
                    status=status,
                )
                if result:
                    self._update_item_extras(item.id, NC_UID_KEY, child_uid)
            except Exception:
                logger.exception("Failed to push unsynced item '%s' to Nextcloud", summary)

        # Update last sync timestamp
        self._update_list_extras(shopping_list_id, NC_LAST_SYNC_KEY, datetime.now(UTC).isoformat())

    # ─── Full sync (scheduled task) ───────────────────────────────────

    async def full_sync(self) -> None:
        """Full bidirectional sync for all shopping lists. Called by the scheduler."""
        if not self.nc:
            return

        shopping_lists = self._get_all_shopping_lists()
        if not shopping_lists:
            return

        try:
            todos = await self.nc.list_todos()
        except Exception:
            logger.exception("Failed to fetch Nextcloud tasks for full sync")
            return

        for shopping_list in shopping_lists:
            # Re-fetch full list with items
            full_list = self._get_shopping_list(shopping_list.id)
            if not full_list:
                continue

            parent_uid = (full_list.extras or {}).get(NC_PARENT_UID_KEY)

            # Check if sync is needed based on updated_at vs last sync
            last_sync_str = (full_list.extras or {}).get(NC_LAST_SYNC_KEY)
            if last_sync_str and parent_uid:
                try:
                    last_sync = datetime.fromisoformat(last_sync_str)
                    if full_list.updated_at and full_list.updated_at <= last_sync:
                        # Check if NC side has changes
                        nc_children = [t for t in todos if t.parent_uid == parent_uid]
                        nc_has_changes = False
                        for todo in nc_children:
                            if todo.last_modified:
                                try:
                                    mod_time = datetime.strptime(todo.last_modified, "%Y%m%dT%H%M%SZ").replace(
                                        tzinfo=UTC
                                    )
                                    if mod_time > last_sync:
                                        nc_has_changes = True
                                        break
                                except ValueError:
                                    nc_has_changes = True
                                    break

                        # Also check for new items in NC that we don't know about
                        known_nc_uids = set()
                        for item in full_list.list_items:
                            nc_uid = _get_nc_uid(item.extras)
                            if nc_uid:
                                known_nc_uids.add(nc_uid)
                        for todo in nc_children:
                            if todo.uid not in known_nc_uids:
                                nc_has_changes = True
                                break

                        if not nc_has_changes:
                            logger.debug("Skipping sync for list '%s' - no changes detected", full_list.name)
                            continue
                except (ValueError, TypeError):
                    pass  # Invalid timestamp, do full sync

            # Perform pull (which also pushes unsynced items)
            await self.pull_changes(shopping_list.id)
