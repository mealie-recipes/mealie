from mealie.schema._mealie import MealieModel


class MaintenanceSummary(MealieModel):
    data_dir_size: str
    log_file_size: str
    cleanable_images: int
    cleanable_dirs: int


class MaintenanceLogs(MealieModel):
    logs: list[str]
