from pydantic import UUID4, ConfigDict
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.household.household import Household
from mealie.db.models.household.preferences import HouseholdPreferencesModel
from mealie.schema._mealie import MealieModel


class UpdateHouseholdPreferences(MealieModel):
    private_household: bool = True
    lock_recipe_edits_from_other_households: bool = True
    first_day_of_week: int = 0

    # Recipe Defaults
    recipe_public: bool = True
    recipe_show_nutrition: bool = False
    recipe_show_assets: bool = False
    recipe_landscape_view: bool = False
    recipe_disable_comments: bool = False
    recipe_disable_amount: bool = True


class CreateHouseholdPreferences(UpdateHouseholdPreferences): ...


class SaveHouseholdPreferences(UpdateHouseholdPreferences):
    household_id: UUID4


class ReadHouseholdPreferences(CreateHouseholdPreferences):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            joinedload(HouseholdPreferencesModel.household).load_only(Household.group_id),
        ]
