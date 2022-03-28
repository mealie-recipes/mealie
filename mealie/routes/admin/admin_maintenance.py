import contextlib
import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException

from mealie.core.root_logger import LOGGER_FILE
from mealie.pkgs.stats import fs_stats
from mealie.routes._base import BaseAdminController, controller
from mealie.schema.admin import MaintenanceSummary
from mealie.schema.admin.maintenance import MaintenanceLogs, MaintenanceStorageDetails
from mealie.schema.response import ErrorResponse, SuccessResponse

router = APIRouter(prefix="/maintenance")


def clean_images(root_dir: Path, dry_run: bool) -> int:
    cleaned_images = 0

    for recipe_dir in root_dir.iterdir():
        image_dir = recipe_dir.joinpath("images")

        if not image_dir.exists():
            continue

        for image in image_dir.iterdir():
            if image.is_dir():
                continue

            if image.suffix != ".webp":
                if not dry_run:
                    image.unlink()

                cleaned_images += 1

    return cleaned_images


def clean_recipe_folders(root_dir: Path, dry_run: bool) -> int:
    cleaned_dirs = 0

    for recipe_dir in root_dir.iterdir():
        if recipe_dir.is_dir():
            # Attemp to convert the folder name to a UUID
            try:
                uuid.UUID(recipe_dir.name)
                continue
            except ValueError:
                if not dry_run:
                    shutil.rmtree(recipe_dir)
                cleaned_dirs += 1

    return cleaned_dirs


def tail_log(log_file: Path, n: int) -> list[str]:
    try:
        with open(log_file, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return ["no log file found"]

    return lines[-n:]


@controller(router)
class AdminMaintenanceController(BaseAdminController):
    @router.get("", response_model=MaintenanceSummary)
    def get_maintenance_summary(self):
        """
        Get the maintenance summary
        """
        log_file_size = 0
        with contextlib.suppress(FileNotFoundError):
            log_file_size = os.path.getsize(LOGGER_FILE)

        return MaintenanceSummary(
            data_dir_size=fs_stats.pretty_size(fs_stats.get_dir_size(self.deps.folders.DATA_DIR)),
            log_file_size=fs_stats.pretty_size(log_file_size),
            cleanable_images=clean_images(self.deps.folders.RECIPE_DATA_DIR, dry_run=True),
            cleanable_dirs=clean_recipe_folders(self.deps.folders.RECIPE_DATA_DIR, dry_run=True),
        )

    @router.get("/storage", response_model=MaintenanceStorageDetails)
    def get_storage_details(self):
        return MaintenanceStorageDetails(
            temp_dir_size=fs_stats.pretty_size(fs_stats.get_dir_size(self.deps.folders.TEMP_DIR)),
            backups_dir_size=fs_stats.pretty_size(fs_stats.get_dir_size(self.deps.folders.BACKUP_DIR)),
            groups_dir_size=fs_stats.pretty_size(fs_stats.get_dir_size(self.deps.folders.GROUPS_DIR)),
            recipes_dir_size=fs_stats.pretty_size(fs_stats.get_dir_size(self.deps.folders.RECIPE_DATA_DIR)),
            user_dir_size=fs_stats.pretty_size(fs_stats.get_dir_size(self.deps.folders.USER_DIR)),
        )

    @router.post("/clean/images", response_model=SuccessResponse)
    def clean_images(self):
        """
        Purges all the images from the filesystem that aren't .webp
        """
        try:
            cleaned_images = clean_images(self.deps.folders.RECIPE_DATA_DIR, dry_run=False)
            return SuccessResponse.respond(f"{cleaned_images} Images cleaned")
        except Exception as e:
            raise HTTPException(status_code=500, detail=ErrorResponse.respond("Failed to clean images")) from e

    @router.post("/clean/recipe-folders", response_model=SuccessResponse)
    def clean_recipe_folders(self):
        """
        Deletes all the recipe folders that don't have names that are valid UUIDs
        """
        try:
            cleaned_dirs = clean_recipe_folders(self.deps.folders.RECIPE_DATA_DIR, dry_run=False)
            return SuccessResponse.respond(f"{cleaned_dirs} Recipe folders removed")
        except Exception as e:
            raise HTTPException(status_code=500, detail=ErrorResponse.respond("Failed to clean directories")) from e

    @router.post("/clean/logs", response_model=SuccessResponse)
    def clean_logs(self):
        """
        Purges the logs
        """
        try:
            with contextlib.suppress(FileNotFoundError):
                os.remove(LOGGER_FILE)
                LOGGER_FILE.touch()
            return SuccessResponse.respond("Logs cleaned")
        except Exception as e:
            raise HTTPException(status_code=500, detail=ErrorResponse.respond("Failed to clean logs")) from e

    @router.get("/logs", response_model=MaintenanceLogs)
    def get_logs(self, lines: int = 200):

        return MaintenanceLogs(logs=tail_log(LOGGER_FILE, lines))
