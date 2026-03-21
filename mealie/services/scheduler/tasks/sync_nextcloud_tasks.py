"""Scheduled task for bidirectional Nextcloud Tasks sync.

Runs every 5 minutes (registered as minutely) to reconcile shopping list
state between Mealie and Nextcloud CalDAV.
"""

import asyncio
import logging

from mealie.core.config import get_app_settings
from mealie.db.db_setup import session_context
from mealie.repos.all_repositories import get_repositories
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.nextcloud.sync import NextcloudSyncService

logger = logging.getLogger(__name__)


def sync_nextcloud_tasks():
    """Periodic bidirectional sync with change detection."""
    settings = get_app_settings()
    if not settings.NEXTCLOUD_ENABLED:
        return

    with session_context() as session:
        repos = get_repositories(session)
        groups = repos.groups.page_all(PaginationQuery(page=1, per_page=-1)).items

        for group in groups:
            group_repos = get_repositories(session, group_id=group.id)
            households = group_repos.households.page_all(PaginationQuery(page=1, per_page=-1)).items

            for household in households:
                household_repos = get_repositories(session, group_id=group.id, household_id=household.id)
                sync = NextcloudSyncService(household_repos, settings)
                try:
                    asyncio.run(sync.full_sync())
                except Exception:
                    logger.exception(
                        "Nextcloud sync failed for group=%s household=%s",
                        group.name,
                        household.name,
                    )
