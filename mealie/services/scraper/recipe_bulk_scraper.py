from pydantic import UUID4

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import CreateRecipeByUrlBulk
from mealie.schema.reports.reports import ReportCategory, ReportCreate, ReportEntryCreate, ReportSummaryStatus
from mealie.schema.user.user import GroupInDB
from mealie.services._base_service import BaseService
from mealie.services.recipe.recipe_service import RecipeService
from mealie.services.scraper.scraper import create_from_url


class RecipeBulkScraperService(BaseService):
    report_entries: list[ReportEntryCreate]

    def __init__(self, service: RecipeService, repos: AllRepositories, group: GroupInDB) -> None:
        self.service = service
        self.repos = repos
        self.group = group
        self.report_entries = []

        super().__init__()

    def get_report_id(self) -> UUID4:
        import_report = ReportCreate(
            name="Bulk Import",
            category=ReportCategory.bulk_import,
            status=ReportSummaryStatus.in_progress,
            group_id=self.group.id,
        )

        self.report = self.repos.group_reports.create(import_report)
        return self.report.id

    def _add_error_entry(self, message: str, exception: str = "") -> None:
        self.report_entries.append(
            ReportEntryCreate(
                report_id=self.report.id,
                success=False,
                message=message,
                exception=exception,
            )
        )

    def _save_all_entries(self) -> None:
        is_success = True
        is_failure = True

        for entry in self.report_entries:
            if is_failure and entry.success:
                is_failure = False

            if is_success and not entry.success:
                is_success = False

            self.repos.group_report_entries.create(entry)

        if is_success:
            self.report.status = ReportSummaryStatus.success

        if is_failure:
            self.report.status = ReportSummaryStatus.failure

        if not is_success and not is_failure:
            self.report.status = ReportSummaryStatus.partial

        self.repos.group_reports.update(self.report.id, self.report)

    def scrape(self, urls: CreateRecipeByUrlBulk) -> None:
        if self.report is None:
            self.get_report_id()

        for b in urls.imports:

            try:
                recipe, _ = create_from_url(b.url)
            except Exception as e:
                self.service.logger.error(f"failed to scrape url during bulk url import {b.url}")
                self.service.logger.exception(e)
                self._add_error_entry(f"failed to scrape url {b.url}", str(e))
                continue

            if b.tags:
                recipe.tags = b.tags

            if b.categories:
                recipe.recipe_category = b.categories

            try:
                self.service.create_one(recipe)
            except Exception as e:
                self.service.logger.error(f"Failed to save recipe to database during bulk url import {b.url}")
                self.service.logger.exception(e)
                self._add_error_entry(f"Failed to save recipe to database during bulk url import {b.url}", str(e))
                continue

            self.report_entries.append(
                ReportEntryCreate(
                    report_id=self.report.id,
                    success=True,
                    message=f"Successfully imported recipe {recipe.name}",
                    exception="",
                )
            )

        self._save_all_entries()
