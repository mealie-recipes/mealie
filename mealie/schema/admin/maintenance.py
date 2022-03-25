from fastapi_camelcase import CamelModel


class MaintenanceSummary(CamelModel):
    data_dir_size: str
    log_file_size: str
    cleanable_images: int
    cleanable_dirs: int
