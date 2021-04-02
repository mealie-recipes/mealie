from fastapi_camelcase import CamelModel


class AppInfo(CamelModel):
    version: str
    demo_status: bool
