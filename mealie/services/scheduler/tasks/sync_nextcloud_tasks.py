"""Scheduled task for bidirectional Nextcloud Tasks sync.

Runs every 1 minute to reconcile shopping list state between Mealie
and Nextcloud CalDAV, for households that have Nextcloud sync enabled.
"""

import logging

from mealie.db.db_setup import session_context
from mealie.repos.all_repositories import get_repositories
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.nextcloud.sync import NextcloudSyncService, create_nc_service_from_prefs

logger = logging.getLogger(__name__)


def sync_nextcloud_tasks():
    """Periodic bidirectional sync with change detection."""
    with session_context() as session:
        repos = get_repositories(session)
        groups = repos.groups.page_all(PaginationQuery(page=1, per_page=-1)).items

        for group in groups:
            group_repos = get_repositories(session, group_id=group.id)
            households = group_repos.households.page_all(PaginationQuery(page=1, per_page=-1)).items

            for household in households:
                household_repos = get_repositories(session, group_id=group.id, household_id=household.id)

                # Check if Nextcloud sync is enabled for this household
                prefs = household.preferences
                nc = create_nc_service_from_prefs(prefs)
                if not nc:
                    continue

                sync = NextcloudSyncService(household_repos, nc)
                try:
                    sync.full_sync()
                except Exception:
                    logger.exception(
                        "Nextcloud sync failed for group=%s household=%s",
                        group.name,
                        household.name,
                    )
