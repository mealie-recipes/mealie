from pathlib import Path
from fastapi_camelcase import CamelModel


class AppInfo(CamelModel):
    production: bool
    version: str
    demo_status: bool


class DebugInfo(AppInfo):
    api_port: int
    api_docs: bool
    db_url: str
    default_group: str
