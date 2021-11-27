import enum

from fastapi_camelcase import CamelModel


class SupportedMigrations(str, enum.Enum):
    nextcloud = "nextcloud"
    chowdown = "chowdown"


class DataMigrationCreate(CamelModel):
    source_type: SupportedMigrations
