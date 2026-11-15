from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import MealieOutModel


class MaintenanceSummary(MealieOutModel):
    data_dir_size: str
    cleanable_images: int
    cleanable_dirs: int


class MaintenanceStorageDetails(MealieModel):
    temp_dir_size: str
    backups_dir_size: str
    groups_dir_size: str
    recipes_dir_size: str
    user_dir_size: str
