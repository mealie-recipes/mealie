from datetime import date

import pytest

from mealie.schema.meal_plan.plan_rules import PlanRulesDay

test_cases = [
    (date(2022, 2, 7), PlanRulesDay.monday),
    (date(2022, 2, 8), PlanRulesDay.tuesday),
    (date(2022, 2, 9), PlanRulesDay.wednesday),
    (date(2022, 2, 10), PlanRulesDay.thursday),
    (date(2022, 2, 11), PlanRulesDay.friday),
    (date(2022, 2, 12), PlanRulesDay.saturday),
    (date(2022, 2, 13), PlanRulesDay.sunday),
]


@pytest.mark.parametrize("day, expected", test_cases)
def test_date_obj_to_enum(day: date, expected: PlanRulesDay):
    assert PlanRulesDay.from_date(day) == expected
