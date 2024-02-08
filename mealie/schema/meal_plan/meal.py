from datetime import date

from pydantic import ConfigDict, validator

from mealie.schema._mealie import MealieModel


class MealIn(MealieModel):
    slug: str | None
    name: str | None
    description: str | None
    model_config = ConfigDict(from_attributes=True)


class MealDayIn(MealieModel):
    date: date | None
    meals: list[MealIn]
    model_config = ConfigDict(from_attributes=True)


class MealDayOut(MealDayIn):
    id: int
    model_config = ConfigDict(from_attributes=True)


class MealPlanIn(MealieModel):
    group: str
    start_date: date
    end_date: date
    plan_days: list[MealDayIn]

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("end_date")
    def end_date_after_start_date(v, values, config, field):
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("EndDate should be greater than StartDate")
        return v

    model_config = ConfigDict(from_attributes=True)


class MealPlanOut(MealPlanIn):
    id: int
    shopping_list: int | None
    model_config = ConfigDict(from_attributes=True)
