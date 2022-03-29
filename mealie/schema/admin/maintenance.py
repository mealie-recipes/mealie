from mealie.schema._mealie import MealieModel


class MaintenanceSummary(MealieModel):
    data_dir_size: str
    log_file_size: str
    cleanable_images: int
    cleanable_dirs: int


class MaintenanceStorageDetails(MealieModel):
    temp_dir_size: str
    backups_dir_size: str
    groups_dir_size: str
    recipes_dir_size: str
    user_dir_size: str


class MaintenanceLogs(MealieModel):
    logs: list[str]
