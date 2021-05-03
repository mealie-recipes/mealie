from pathlib import Path

from fastapi_camelcase import CamelModel

class AppStatistics(CamelModel):
    total_recipes: int
    total_users: int
    total_groups: int
    uncategorized_recipes: int
    untagged_recipes: int


class AppInfo(CamelModel):
    production: bool
    version: str
    demo_status: bool


class DebugInfo(AppInfo):
    api_port: int
    api_docs: bool
    db_type: str
    db_url: Path
    default_group: str
