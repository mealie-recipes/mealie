from fastapi_camelcase import CamelModel


class GetAll(CamelModel):
    start: int = 0
    limit: int = 999
