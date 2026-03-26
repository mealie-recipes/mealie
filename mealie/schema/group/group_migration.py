import enum

from mealie.schema._mealie import MealieModel


class SupportedMigrations(enum.StrEnum):
    nextcloud = "nextcloud"
    chowdown = "chowdown"
    copymethat = "copymethat"
    paprika = "paprika"
    mealie_alpha = "mealie_alpha"
    tandoor = "tandoor"
    plantoeat = "plantoeat"
    myrecipebox = "myrecipebox"
    recipekeeper = "recipekeeper"
    cookn = "cookn"


class DataMigrationCreate(MealieModel):
    source_type: SupportedMigrations
