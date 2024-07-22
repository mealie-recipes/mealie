from pydantic import UUID4, ConfigDict

from mealie.schema._mealie import MealieModel


class UpdateHouseholdPreferences(MealieModel):
    private_household: bool = True
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
