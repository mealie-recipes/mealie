from mealie.schema._mealie import MealieModel


class Nutrition(MealieModel):
    calories: str | None
    fat_content: str | None
    protein_content: str | None
    carbohydrate_content: str | None
    fiber_content: str | None
    sodium_content: str | None
    sugar_content: str | None

    class Config:
        orm_mode = True
