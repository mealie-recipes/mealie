"""Bidirectional sync between Mealie shopping lists and Nextcloud Tasks.

Each Mealie ShoppingList maps to a parent VTODO in a single configured Nextcloud task list.
Each ShoppingListItem maps to a child VTODO linked via RELATED-TO;RELTYPE=PARENT.
UID mapping is tracked via the extras dict on ShoppingList and ShoppingListItem.

All methods are fully synchronous.
"""

import logging
from datetime import UTC, datetime
from typing import cast
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.orm.session import Session

from mealie.db.models.household.shopping_list import ShoppingList, ShoppingListItem
from mealie.db.models.recipe.api_extras import ShoppingListExtras, ShoppingListItemExtras
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
    if not extras:
        return None
    return extras.get(NC_UID_KEY)


def _set_extra(session: Session, model_cls, fk_column: str, fk_id, key: str, value: str) -> None:
    """Set an extras key-value directly via SQL, avoiding full-object update issues."""
    # Check if key already exists
    stmt = select(model_cls).where(
        getattr(model_cls, fk_column) == fk_id,
        model_cls.key_name == key,
    )
    existing = session.execute(stmt).scalar_one_or_none()
    if existing:
        existing.value = value
    else:
        new_extra = model_cls(key=key, value=value)
        setattr(new_extra, fk_column, fk_id)
        session.add(new_extra)
    session.commit()


def create_nc_service_from_prefs(prefs) -> NextcloudTasksService | None:
    """Create a NextcloudTasksService from household preferences."""
    if not prefs or not prefs.nextcloud_enabled:
        return None
    if not all([prefs.nextcloud_url, prefs.nextcloud_username, prefs.nextcloud_password, prefs.nextcloud_task_list]):
        return None
    return NextcloudTasksService(
        url=prefs.nextcloud_url,
        username=prefs.nextcloud_username,
        password=prefs.nextcloud_password,
        task_list=prefs.nextcloud_task_list,
        verify_ssl=prefs.nextcloud_verify_ssl if prefs.nextcloud_verify_ssl is not None else True,
    )


class NextcloudSyncService:
    """Bidirectional sync between Mealie shopping lists and Nextcloud Tasks."""

    def __init__(self, repos: AllRepositories, nc: NextcloudTasksService | None = None) -> None:
        self.repos = repos
        self.session = repos.session
        self.nc = nc
        self._parent_uid_cache: dict[str, str] = {}

    def _get_shopping_list(self, shopping_list_id: UUID4) -> ShoppingListOut | None:
        return cast(ShoppingListOut | None, self.repos.group_shopping_lists.get_one(shopping_list_id))

    def _get_all_shopping_lists(self) -> list[ShoppingListSummary]:
        result = self.repos.group_shopping_lists.page_all(
            PaginationQuery(page=1, per_page=-1),
            override=ShoppingListSummary,
        )
        return result.items

    def _set_list_extra(self, list_id: UUID4, key: str, value: str) -> None:
        """Set an extra on a shopping list via direct SQL."""
        _set_extra(self.session, ShoppingListExtras, "shopping_list_id", list_id, key, value)

    def _set_item_extra(self, item_id: UUID4, key: str, value: str) -> None:
        """Set an extra on a shopping list item via direct SQL."""
        _set_extra(self.session, ShoppingListItemExtras, "shopping_list_item_id", item_id, key, value)

    def _get_list_extra(self, list_id: UUID4, key: str) -> str | None:
        """Get an extra value from a shopping list."""
        stmt = select(ShoppingListExtras).where(
            ShoppingListExtras.shopping_list_id == list_id,
            ShoppingListExtras.key_name == key,
        )
        result = self.session.execute(stmt).scalar_one_or_none()
        return result.value if result else None

    def _ensure_parent(self, shopping_list: ShoppingListOut) -> str | None:
        """Ensure a parent VTODO exists for the shopping list. Returns parent_uid or None."""
        if not self.nc:
            return None

        list_id_str = str(shopping_list.id)

        # Check in-memory cache first (avoids race between push and pull in same request)
        if list_id_str in self._parent_uid_cache:
            return self._parent_uid_cache[list_id_str]

        # Read parent UID directly from DB
        self.session.expire_all()  # ensure fresh read
        parent_uid = self._get_list_extra(shopping_list.id, NC_PARENT_UID_KEY)
        if parent_uid:
            self._parent_uid_cache[list_id_str] = parent_uid
            return parent_uid

        parent_uid = str(uuid4())
        result = self.nc.create_todo(
            summary=shopping_list.name or "Shopping List",
            uid=parent_uid,
        )
        if result:
            self._set_list_extra(shopping_list.id, NC_PARENT_UID_KEY, parent_uid)
            self._parent_uid_cache[list_id_str] = parent_uid
            logger.info("Created Nextcloud parent task for list '%s'", shopping_list.name)
            return parent_uid

        logger.error("Failed to create parent task for list '%s'", shopping_list.name)
        return None

    # ─── Push operations (Mealie → Nextcloud) ─────────────────────────

    def push_items_created(self, shopping_list_id: UUID4, item_ids: list[UUID4]) -> None:
        """Push newly created items to Nextcloud as child VTODOs."""
        if not self.nc:
            return

        shopping_list = self._get_shopping_list(shopping_list_id)
        if not shopping_list:
            return

        parent_uid = self._ensure_parent(shopping_list)
        if not parent_uid:
            return

        for item_id in item_ids:
            item = cast(ShoppingListItemOut | None, self.repos.group_shopping_list_item.get_one(item_id))
            if not item:
                continue

            # Skip if already synced — check directly from DB
            stmt = select(ShoppingListItemExtras).where(
                ShoppingListItemExtras.shopping_list_item_id == item_id,
                ShoppingListItemExtras.key_name == NC_UID_KEY,
            )
            if self.session.execute(stmt).scalar_one_or_none():
                continue

            summary = _item_to_summary(item)
            child_uid = str(uuid4())
            try:
                status = "COMPLETED" if item.checked else "NEEDS-ACTION"
                result = self.nc.create_todo(
                    summary=summary,
                    parent_uid=parent_uid,
                    uid=child_uid,
                    status=status,
                )
                if result:
                    self._set_item_extra(item_id, NC_UID_KEY, child_uid)
            except Exception:
                logger.exception("Failed to push item '%s' to Nextcloud", summary)

    def push_items_updated(self, shopping_list_id: UUID4, item_ids: list[UUID4]) -> None:
        """Push item updates (including check status) to Nextcloud."""
        if not self.nc:
            return

        for item_id in item_ids:
            item = cast(ShoppingListItemOut | None, self.repos.group_shopping_list_item.get_one(item_id))
            if not item:
                continue

            nc_uid = _get_nc_uid(item.extras)
            if not nc_uid:
                self.push_items_created(shopping_list_id, [item_id])
                continue

            try:
                summary = _item_to_summary(item)
                self.nc.update_todo_summary(nc_uid, summary)
                if item.checked:
                    self.nc.complete_todo(nc_uid)
                else:
                    self.nc.uncomplete_todo(nc_uid)
            except Exception:
                logger.exception("Failed to update item '%s' in Nextcloud", nc_uid)

    def push_items_deleted_by_nc_uids(self, nc_uids: list[str]) -> None:
        """Delete VTODOs from Nextcloud by their UIDs."""
        if not self.nc:
            return
        for nc_uid in nc_uids:
            try:
                self.nc.delete_todo(nc_uid)
            except Exception:
                logger.exception("Failed to delete VTODO '%s' from Nextcloud", nc_uid)

    # ─── Pull operations (Nextcloud → Mealie) ─────────────────────────

    def pull_changes(self, shopping_list_id: UUID4) -> None:
        """Pull changes from Nextcloud for a specific shopping list."""
        if not self.nc:
            return

        shopping_list = self._get_shopping_list(shopping_list_id)
        if not shopping_list:
            return

        parent_uid = self._ensure_parent(shopping_list)
        if not parent_uid:
            return

        try:
            todos = self.nc.list_todos()
        except Exception:
            logger.exception("Failed to fetch Nextcloud tasks for pull")
            return

        # Find children of this parent
        nc_children = {t.uid: t for t in todos if t.parent_uid == parent_uid}
        logger.info(
            "Pull: list='%s' parent_uid=%s, NC children=%d, total NC todos=%d",
            shopping_list.name, parent_uid, len(nc_children), len(todos),
        )

        # Re-read the list with fresh session data
        self.session.expire_all()
        shopping_list = self._get_shopping_list(shopping_list_id)
        if not shopping_list:
            return

        # Build set of all NC child UIDs for quick lookup
        all_nc_child_uids = set(nc_children.keys())

        # Build map of existing Mealie items by their NC UID
        mealie_items_by_nc_uid: dict[str, ShoppingListItemOut] = {}
        mealie_items_without_nc: list[ShoppingListItemOut] = []
        for item in shopping_list.list_items:
            nc_uid = _get_nc_uid(item.extras)
            if nc_uid:
                mealie_items_by_nc_uid[nc_uid] = item
            else:
                mealie_items_without_nc.append(item)

        # 1. Sync check status and summary from Nextcloud → Mealie
        for nc_uid, todo in nc_children.items():
            mealie_item = mealie_items_by_nc_uid.get(nc_uid)
            if not mealie_item:
                continue

            needs_update = False
            updated_item = mealie_item.cast(ShoppingListItemUpdateBulk, id=mealie_item.id)

            # Sync check status
            nc_is_completed = todo.status in ("COMPLETED", "DONE")
            if nc_is_completed != mealie_item.checked:
                updated_item.checked = nc_is_completed
                needs_update = True
                logger.info("Synced check status for '%s': checked=%s", todo.summary, nc_is_completed)

            # Sync summary: compare NC summary with what Mealie would generate
            mealie_summary = _item_to_summary(mealie_item)
            if todo.summary != mealie_summary:
                # NC summary was changed — update Mealie's note to match
                # Only update if the item was originally created from NC (no food/unit)
                # or if the NC summary clearly differs from what Mealie generated
                updated_item.note = todo.summary
                needs_update = True
                logger.info("Synced summary from NC: '%s' -> '%s'", mealie_summary, todo.summary)

            if needs_update:
                try:
                    self.repos.group_shopping_list_item.update(mealie_item.id, updated_item)
                except Exception:
                    logger.exception("Failed to sync item '%s'", todo.summary)

        # 2. Import NC tasks that don't exist in Mealie
        known_nc_uids = set(mealie_items_by_nc_uid.keys())
        new_from_nc = [uid for uid in nc_children if uid not in known_nc_uids]
        logger.info("Pull: known_nc_uids=%d, new_from_nc=%d, mealie_without_nc=%d",
                     len(known_nc_uids), len(new_from_nc), len(mealie_items_without_nc))
        for nc_uid, todo in nc_children.items():
            if nc_uid in known_nc_uids:
                continue
            if todo.status in ("COMPLETED", "DONE"):
                continue

            new_item = ShoppingListItemCreate(
                shopping_list_id=shopping_list_id,
                note=todo.summary,
                checked=False,
                quantity=0,
                is_ingredient=False,
                extras={NC_UID_KEY: nc_uid},
            )
            try:
                created = self.repos.group_shopping_list_item.create(new_item)
                if created:
                    logger.info("Imported from Nextcloud: '%s'", todo.summary)
            except Exception:
                logger.exception("Failed to import NC task '%s'", todo.summary)

        # 3. Push Mealie items that aren't in Nextcloud yet
        #    But first re-check extras from DB — another request may have set nc_uid
        for item in mealie_items_without_nc:
            # Double-check: maybe nc_uid was set by a concurrent push
            stmt = select(ShoppingListItemExtras).where(
                ShoppingListItemExtras.shopping_list_item_id == item.id,
                ShoppingListItemExtras.key_name == NC_UID_KEY,
            )
            existing_extra = self.session.execute(stmt).scalar_one_or_none()
            if existing_extra and existing_extra.value:
                logger.debug("Skipping push for '%s' — nc_uid already set by push", _item_to_summary(item))
                continue

            # Also check if NC already has a matching VTODO (dedup by summary)
            summary = _item_to_summary(item)
            already_in_nc = False
            for nc_uid, todo in nc_children.items():
                if nc_uid not in known_nc_uids and todo.summary == summary:
                    # Match found — link them instead of creating a duplicate
                    self._set_item_extra(item.id, NC_UID_KEY, nc_uid)
                    known_nc_uids.add(nc_uid)
                    already_in_nc = True
                    logger.info("Linked existing NC task '%s' to Mealie item", summary)
                    break

            if already_in_nc:
                continue

            child_uid = str(uuid4())
            status = "COMPLETED" if item.checked else "NEEDS-ACTION"
            try:
                result = self.nc.create_todo(
                    summary=summary,
                    parent_uid=parent_uid,
                    uid=child_uid,
                    status=status,
                )
                if result:
                    self._set_item_extra(item.id, NC_UID_KEY, child_uid)
            except Exception:
                logger.exception("Failed to push item '%s' to Nextcloud", summary)

        self._set_list_extra(shopping_list_id, NC_LAST_SYNC_KEY, datetime.now(UTC).isoformat())

    # ─── Full sync (scheduled task) ───────────────────────────────────

    def full_sync(self) -> None:
        """Full bidirectional sync for all shopping lists."""
        if not self.nc:
            return

        shopping_lists = self._get_all_shopping_lists()
        if not shopping_lists:
            return

        for shopping_list in shopping_lists:
            # Check if sync is needed
            last_sync_str = self._get_list_extra(shopping_list.id, NC_LAST_SYNC_KEY)
            if last_sync_str:
                try:
                    last_sync = datetime.fromisoformat(last_sync_str)
                    full_list = self._get_shopping_list(shopping_list.id)
                    if full_list and full_list.updated_at and full_list.updated_at <= last_sync:
                        # Mealie side hasn't changed, but NC might have — always pull to check
                        pass
                except (ValueError, TypeError):
                    pass

            self.pull_changes(shopping_list.id)
