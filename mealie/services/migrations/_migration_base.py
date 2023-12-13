import contextlib
from pathlib import Path
from uuid import UUID

from pydantic import UUID4

from mealie.core import root_logger
from mealie.core.exceptions import UnexpectedNone
from mealie.repos.all_repositories import AllRepositories
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe_settings import RecipeSettings
from mealie.schema.reports.reports import (
    ReportCategory,
    ReportCreate,
    ReportEntryCreate,
    ReportOut,
    ReportSummary,
    ReportSummaryStatus,
)
from mealie.services.recipe.recipe_service import RecipeService
from mealie.services.scraper import cleaner

from .._base_service import BaseService
from .utils.database_helpers import DatabaseMigrationHelpers
from .utils.migration_alias import MigrationAlias


class BaseMigrator(BaseService):
    key_aliases: list[MigrationAlias]

    report_entries: list[ReportEntryCreate]
    report_id: UUID4
    report: ReportOut

    helpers: DatabaseMigrationHelpers

    def __init__(
        self, archive: Path, db: AllRepositories, session, user_id: UUID4, group_id: UUID, add_migration_tag: bool
    ):
        self.archive = archive
        self.db = db
        self.session = session
        self.add_migration_tag = add_migration_tag

        user = db.users.get_one(user_id)
        if not user:
            raise UnexpectedNone(f"Cannot find user {user_id}")

        group = db.groups.get_one(group_id)
        if not group:
            raise UnexpectedNone(f"Cannot find group {group_id}")

        self.user = user
        self.group = group

        self.name = "migration"

        self.report_entries = []

        self.logger = root_logger.get_logger()

        self.helpers = DatabaseMigrationHelpers(self.db, self.session, self.group.id, self.user.id)
        self.recipe_service = RecipeService(db, user, group)

        super().__init__()

    def _migrate(self) -> None:
        raise NotImplementedError

    def _create_report(self, report_name: str) -> None:
        report_to_save = ReportCreate(
            name=report_name,
            category=ReportCategory.migration,
            status=ReportSummaryStatus.in_progress,
            group_id=self.group.id,
        )

        self.report = self.db.group_reports.create(report_to_save)
        self.report_id = self.report.id

    def _save_all_entries(self) -> None:
        is_success = True
        is_failure = True

        for entry in self.report_entries:
            if is_failure and entry.success:
                is_failure = False

            if is_success and not entry.success:
                is_success = False

            self.db.group_report_entries.create(entry)

        if is_success:
            self.report.status = ReportSummaryStatus.success

        if is_failure:
            self.report.status = ReportSummaryStatus.failure

        if not is_success and not is_failure:
            self.report.status = ReportSummaryStatus.partial

        self.db.group_reports.update(self.report.id, self.report)

    def migrate(self, report_name: str) -> ReportSummary:
        self._create_report(report_name)
        self._migrate()
        self._save_all_entries()

        result = self.db.group_reports.get_one(self.report_id)

        if not result:
            raise ValueError("Report not found")

        return result

    def import_recipes_to_database(self, validated_recipes: list[Recipe]) -> list[tuple[str, UUID4, bool]]:
        """
        Used as a single access point to process a list of Recipe objects into the
        database in a predictable way. If an error occurs the session is rolled back
        and the process will continue. All import information is appended to the
        'migration_report' attribute to be returned to the frontend for display.

        Args:
            validated_recipes (list[Recipe]):
        """
        if self.add_migration_tag:
            migration_tag = self.helpers.get_or_set_tags([self.name])[0]

        return_vars: list[tuple[str, UUID4, bool]] = []

        if not self.group.preferences:
            raise ValueError("Group preferences not found")

        default_settings = RecipeSettings(
            public=self.group.preferences.recipe_public,
            show_nutrition=self.group.preferences.recipe_show_nutrition,
            show_assets=self.group.preferences.recipe_show_assets,
            landscape_view=self.group.preferences.recipe_landscape_view,
            disable_comments=self.group.preferences.recipe_disable_comments,
            disable_amount=self.group.preferences.recipe_disable_amount,
        )

        for recipe in validated_recipes:
            recipe.settings = default_settings

            recipe.user_id = self.user.id
            recipe.group_id = self.group.id

            if recipe.tags:
                recipe.tags = self.helpers.get_or_set_tags(x.name for x in recipe.tags)
            else:
                recipe.tags = []

            if recipe.recipe_category:
                recipe.recipe_category = self.helpers.get_or_set_category(x.name for x in recipe.recipe_category)

            if self.add_migration_tag:
                recipe.tags.append(migration_tag)

            exception: str | Exception = ""
            status = False
            try:
                recipe = self.recipe_service.create_one(recipe)
                status = True

            except Exception as inst:
                exception = str(inst)
                self.logger.exception(inst)
                self.session.rollback()

            if status:
                message = f"Imported {recipe.name} successfully"
            else:
                message = f"Failed to import {recipe.name}"

            return_vars.append((recipe.slug, recipe.id, status))  # type: ignore

            self.report_entries.append(
                ReportEntryCreate(
                    report_id=self.report_id,
                    success=status,
                    message=message,
                    exception=str(exception),
                )
            )

        return return_vars

    def rewrite_alias(self, recipe_dict: dict) -> dict:
        """A helper function to reassign attributes by an alias using a list
        of MigrationAlias objects to rewrite the alias attribute found in the recipe_dict
        to a

        Args:
            recipe_dict (dict): [description]
            key_aliases (list[MigrationAlias]): [description]

        Returns:
            dict: [description]
        """
        if not self.key_aliases:
            return recipe_dict

        for alias in self.key_aliases:
            try:
                prop_value = recipe_dict.pop(alias.alias)
            except KeyError:
                continue

            if alias.func:
                try:
                    prop_value = alias.func(prop_value)
                except Exception as e:
                    self.logger.exception(e)
                    continue

            recipe_dict[alias.key] = prop_value

        return recipe_dict

    def clean_recipe_dictionary(self, recipe_dict: dict) -> Recipe:
        """
        Calls the rewrite_alias function and the Cleaner.clean function on a
        dictionary and returns the result unpacked into a Recipe object
        """
        recipe_dict = self.rewrite_alias(recipe_dict)

        with contextlib.suppress(KeyError):
            del recipe_dict["id"]

        recipe_dict = cleaner.clean(recipe_dict, url=recipe_dict.get("org_url", None))

        return Recipe(**recipe_dict)
