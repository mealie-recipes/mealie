import enum

from fastapi_camelcase import CamelModel


class SupportedMigrations(str, enum.Enum):
    nextcloud = "nextcloud"
    chowdown = "chowdown"
    paprika = "paprika"
    mealie_alpha = "mealie_alpha"


class DataMigrationCreate(CamelModel):
    source_type: SupportedMigrations
