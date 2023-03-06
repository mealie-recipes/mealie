import enum

from mealie.schema._mealie import MealieModel


class SupportedMigrations(str, enum.Enum):
    nextcloud = "nextcloud"
    chowdown = "chowdown"
    copymethat = "copymethat"
    paprika = "paprika"
    mealie_alpha = "mealie_alpha"


class DataMigrationCreate(MealieModel):
    source_type: SupportedMigrations
