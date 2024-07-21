from mealie.schema._mealie.mealie_model import MealieModel


class HouseholdStatistics(MealieModel):
    total_recipes: int
    total_users: int
    total_categories: int
    total_tags: int
    total_tools: int
