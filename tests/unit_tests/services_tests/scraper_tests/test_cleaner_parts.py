from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import pytest

from mealie.lang.providers import local_provider
from mealie.services.scraper import cleaner


@dataclass(slots=True)
class CleanerCase:
    test_id: str
    input: Any
    expected: Any
    exception: Any = None


clean_string_test_cases = (
    CleanerCase(
        test_id="empty_string",
        input="",
        expected="",
    ),
    CleanerCase(
        test_id="html",
        input="<p> Hello World </p>",
        expected="Hello World",
    ),
    CleanerCase(
        test_id="no_change",
        input="Hello World",
        expected="Hello World",
    ),
    CleanerCase(
        test_id="html_with_extra_closing_tag",
        input="<p> Hello World </p></p>",
        expected="Hello World",
    ),
    CleanerCase(
        test_id="multiple_spaces",
        input="Hello         World",
        expected="Hello World",
    ),
    CleanerCase(
        test_id="tabs",
        input="\tHello World\t",
        expected="Hello World",
    ),
    CleanerCase(
        test_id="nbsp",
        input="\xa0Hello World\xa0",
        expected="Hello World",
    ),
    CleanerCase(
        test_id="list",
        input=["Hello World", "Goodbye World"],
        expected="Hello World",
    ),
    CleanerCase(
        test_id="int",
        input=1,
        expected="1",
    ),
)


@pytest.mark.parametrize("case", clean_string_test_cases, ids=(x.test_id for x in clean_string_test_cases))
def test_cleaner_clean_string(case: CleanerCase) -> None:
    assert case.expected == cleaner.clean_string(case.input)


image_cleaner_test_cases = (
    CleanerCase(
        test_id="empty_string",
        input="",
        expected=["no image"],
    ),
    CleanerCase(
        test_id="no_change",
        input="https://example.com/image.jpg",
        expected=["https://example.com/image.jpg"],
    ),
    CleanerCase(
        test_id="dict with url key",
        input={"url": "https://example.com/image.jpg"},
        expected=["https://example.com/image.jpg"],
    ),
    CleanerCase(
        test_id="list of strings",
        input=["https://example.com/image.jpg"],
        expected=["https://example.com/image.jpg"],
    ),
    CleanerCase(
        test_id="list of dicts with url key",
        input=[{"url": "https://example.com/image.jpg"}],
        expected=["https://example.com/image.jpg"],
    ),
)


@pytest.mark.parametrize("case", image_cleaner_test_cases, ids=(x.test_id for x in image_cleaner_test_cases))
def test_cleaner_image_cleaner(case: CleanerCase):
    result = cleaner.clean_image(case.input)
    assert case.expected == result


instruction_test_cases = (
    CleanerCase(
        test_id="single string",
        input="Instruction A\nInstruction B\nInstruction C",
        expected=None,
    ),
    CleanerCase(
        test_id="single string multiple newlines",
        input="Instruction A\n\nInstruction B\n\nInstruction C",
        expected=None,
    ),
    CleanerCase(
        test_id="common list of dicts",
        input=[
            {"text": "Instruction A"},
            {"text": "Instruction B"},
            {"text": "Instruction C"},
        ],
        expected=None,
    ),
    CleanerCase(
        test_id="dict with int keys",
        input={
            0: {"text": "Instruction A"},
            1: {"text": "Instruction B"},
            2: {"text": "Instruction C"},
        },
        expected=None,
    ),
    CleanerCase(
        test_id="dict with str num keys",
        input={
            "0": {"text": "Instruction A"},
            "1": {"text": "Instruction B"},
            "2": {"text": "Instruction C"},
        },
        expected=None,
    ),
    CleanerCase(
        test_id="dict with str num keys",
        input={
            "1": {"text": "Instruction A"},
            "2": {"text": "Instruction B"},
            "3": {"text": "Instruction C"},
        },
        expected=None,
    ),
    CleanerCase(
        test_id="dict with str num keys",
        input={
            1: {"text": "Instruction A"},
            2: {"text": "Instruction B"},
            3: {"text": "Instruction C"},
        },
        expected=None,
    ),
    CleanerCase(
        test_id="raw json str",
        input='{"0": {"text": "Instruction A"}, "1": {"text": "Instruction B"}, "2": {"text": "Instruction C"}}',
        expected=None,
    ),
    CleanerCase(
        test_id="how to steps",
        input=[
            {
                "@type": "HowToSection",
                "itemListElement": [
                    {
                        "@type": "HowToStep",
                        "text": "Instruction A",
                    },
                    {
                        "@type": "HowToStep",
                        "text": "Instruction B",
                    },
                ],
            },
            {
                "@type": "HowToSection",
                "itemListElement": [
                    {
                        "@type": "HowToStep",
                        "text": "Instruction C",
                    },
                ],
            },
        ],
        expected=None,
    ),
    CleanerCase(
        test_id="excessive whitespace str (1)",
        input="Instruction A\n\nInstruction B\n\nInstruction C\n\n",
        expected=None,
    ),
    CleanerCase(
        test_id="excessive whitespace str (2)",
        input="Instruction A\nInstruction B\nInstruction C\n",
        expected=None,
    ),
    CleanerCase(
        test_id="excessive whitespace str (3)",
        input="Instruction A\r\n\r\nInstruction B\r\n\r\nInstruction C\r\n\r\n",
        expected=None,
    ),
    CleanerCase(
        test_id="excessive whitespace str (4)",
        input="Instruction A\r\nInstruction B\r\nInstruction C\r\n",
        expected=None,
    ),
)


@pytest.mark.parametrize("instructions", instruction_test_cases, ids=(x.test_id for x in instruction_test_cases))
def test_cleaner_instructions(instructions: CleanerCase):
    reuslt = cleaner.clean_instructions(instructions.input)

    expected = [
        {"text": "Instruction A"},
        {"text": "Instruction B"},
        {"text": "Instruction C"},
    ]

    assert reuslt == expected


ingredients_test_cases = (
    CleanerCase(
        input="",
        expected=[],
        test_id="empty string",
    ),
    CleanerCase(
        input="1 cup of flour",
        expected=["1 cup of flour"],
        test_id="single ingredient string",
    ),
    CleanerCase(
        input=["1 cup of flour"],
        expected=["1 cup of flour"],
        test_id="single ingredient list",
    ),
    CleanerCase(
        input=["1 cup of flour", "1 cup of sugar"],
        expected=["1 cup of flour", "1 cup of sugar"],
        test_id="multiple ingredient list",
    ),
    CleanerCase(
        input={"0": "1 cup of flour", "1": "1 cup of sugar"},
        expected=None,
        test_id="multiple ingredient dictionary",
        exception=TypeError,
    ),
)


@pytest.mark.parametrize("ingredients", ingredients_test_cases, ids=(x.test_id for x in ingredients_test_cases))
def test_cleaner_clean_ingredients(ingredients: CleanerCase):
    if ingredients.exception:
        with pytest.raises(ingredients.exception):
            cleaner.clean_ingredients(ingredients.input)

        return

    assert ingredients.expected == cleaner.clean_ingredients(ingredients.input)


yield_test_cases = (
    CleanerCase(
        test_id="empty string",
        input="",
        expected=(0, 0, ""),
    ),
    CleanerCase(
        test_id="regular string",
        input="4 Batches",
        expected=(0, 4, "Batches"),
    ),
    CleanerCase(
        test_id="regular serving string",
        input="4 Servings",
        expected=(4, 0, ""),
    ),
    CleanerCase(
        test_id="regular string with whitespace",
        input="4   Batches    ",
        expected=(0, 4, "Batches"),
    ),
    CleanerCase(
        test_id="regular serving string with whitespace",
        input="4   Servings    ",
        expected=(4, 0, ""),
    ),
    CleanerCase(
        test_id="list of strings",
        input=["Serves 2", "4 Batches", "5 Batches"],
        expected=(2, 5, "Batches"),
    ),
    CleanerCase(
        test_id="basic string",
        input="Makes a lot of Batches",
        expected=(0, 0, "Makes a lot of Batches"),
    ),
    CleanerCase(
        test_id="basic serving string",
        input="Makes 4 Batches",
        expected=(4, 0, ""),
    ),
    CleanerCase(
        test_id="empty list",
        input=[],
        expected=(0, 0, ""),
    ),
    CleanerCase(
        test_id="basic fraction",
        input="1/2 Batches",
        expected=(0, 0.5, "Batches"),
    ),
    CleanerCase(
        test_id="mixed fraction",
        input="1 1/2 Batches",
        expected=(0, 1.5, "Batches"),
    ),
    CleanerCase(
        test_id="improper fraction",
        input="11/2 Batches",
        expected=(0, 5.5, "Batches"),
    ),
    CleanerCase(
        test_id="vulgar fraction",
        input="¾ Batches",
        expected=(0, 0.75, "Batches"),
    ),
    CleanerCase(
        test_id="mixed vulgar fraction",
        input="2¾ Batches",
        expected=(0, 2.75, "Batches"),
    ),
    CleanerCase(
        test_id="mixed vulgar fraction with space",
        input="2 ¾ Batches",
        expected=(0, 2.75, "Batches"),
    ),
    CleanerCase(
        test_id="basic decimal",
        input="0.5 Batches",
        expected=(0, 0.5, "Batches"),
    ),
    CleanerCase(
        test_id="text with numbers",
        input="6 Batches or 10 Batches",
        expected=(0, 6, "Batches or 10 Batches"),
    ),
    CleanerCase(
        test_id="no qty",
        input="A Lot of Servings",
        expected=(0, 0, "A Lot of Servings"),
    ),
    CleanerCase(
        test_id="invalid qty",
        input="1/0 Batches",
        expected=(0, 0, "1/0 Batches"),
    ),
    CleanerCase(
        test_id="int as float",
        input="3.0 Batches",
        expected=(0, 3, "Batches"),
    ),
)


@pytest.mark.parametrize("case", yield_test_cases, ids=(x.test_id for x in yield_test_cases))
def test_cleaner_clean_yield_amount(case: CleanerCase):
    result = cleaner.clean_yield(case.input)
    assert case.expected == result


time_test_cases = (
    CleanerCase(
        test_id="empty string",
        input="",
        expected=None,
    ),
    CleanerCase(
        test_id="emtpy whitespace",
        input=" ",
        expected=None,
    ),
    CleanerCase(
        test_id="none",
        input=None,
        expected=None,
    ),
    CleanerCase(
        test_id="invalid string",
        input="invalid",
        expected="invalid",
    ),
    CleanerCase(
        test_id="timedelta",
        input=timedelta(minutes=30),
        expected="30 minutes",
    ),
    CleanerCase(
        test_id="timedelta string (1)",
        input="PT2H30M",
        expected="2 hours 30 minutes",
    ),
    CleanerCase(
        test_id="timedelta string (2)",
        input="PT30M",
        expected="30 minutes",
    ),
    CleanerCase(
        test_id="timedelta string (3)",
        input="PT2H",
        expected="2 hours",
    ),
    CleanerCase(
        test_id="timedelta string (4)",
        input="P1DT1H1M1S",
        expected="1 day 1 hour 1 minute 1 second",
    ),
    CleanerCase(
        test_id="timedelta string (4)",
        input="P1DT1H1M1.53S",
        expected="1 day 1 hour 1 minute 1 second",
    ),
    CleanerCase(
        test_id="timedelta string (5) invalid",
        input="PT",
        expected="none",
    ),
    CleanerCase(
        test_id="timedelta string (6) PT-3H",
        input="PT-3H",
        expected="PT-3H",
    ),
)


@pytest.mark.parametrize("case", time_test_cases, ids=(x.test_id for x in time_test_cases))
def test_cleaner_clean_time(case: CleanerCase):
    translator = local_provider()
    result = cleaner.clean_time(case.input, translator)
    assert case.expected == result


category_test_cases = (
    CleanerCase(
        test_id="empty string",
        input="",
        expected=[],
    ),
    CleanerCase(
        test_id="emtpy whitespace",
        input=" ",
        expected=[],
    ),
    CleanerCase(
        test_id="emtpy list",
        input=[],
        expected=[],
    ),
    CleanerCase(
        test_id="single string",
        input="Dessert",
        expected=["Dessert"],
    ),
    CleanerCase(
        test_id="nested dictionary",
        input=[
            {"name": "Dessert", "slug": "dessert"},
            {"name": "Lunch", "slug": "lunch"},
        ],
        expected=["Dessert", "Lunch"],
    ),
)


@pytest.mark.parametrize("case", category_test_cases, ids=(x.test_id for x in category_test_cases))
def test_cleaner_clean_categories(case: CleanerCase):
    result = cleaner.clean_categories(case.input)
    assert case.expected == result


tag_test_cases = (
    CleanerCase(
        test_id="empty string",
        input="",
        expected=[],
    ),
    CleanerCase(
        test_id="single tag",
        input="tag",
        expected=["Tag"],
    ),
    CleanerCase(
        test_id="comma separated tags",
        input="tag1, tag2, tag3",
        expected=["Tag1", "Tag2", "Tag3"],
    ),
    CleanerCase(
        test_id="list of tags",
        input=["tag1", "tag2", "tag3"],
        expected=["Tag1", "Tag2", "Tag3"],
    ),
)


@pytest.mark.parametrize("case", tag_test_cases, ids=(x.test_id for x in tag_test_cases))
def test_cleaner_clean_tags(case: CleanerCase):
    result = cleaner.clean_tags(case.input)
    assert case.expected == result


nutrition_test_cases = (
    CleanerCase(
        test_id="empty dict",
        input={},
        expected={},
    ),
    CleanerCase(
        test_id="valid kets",
        input={
            "calories": "100mg",
            "fatContent": "10",
        },
        expected={
            "calories": "100",
            "fatContent": "10",
        },
    ),
    CleanerCase(
        test_id="calories as int",
        input={
            "calories": 100,
        },
        expected={
            "calories": "100",
        },
    ),
    CleanerCase(
        test_id="calories as float",
        input={
            "calories": 100.0,
        },
        expected={
            "calories": "100.0",
        },
    ),
    CleanerCase(
        test_id="invalid keys get removed",
        input={
            "calories": "100mg",
            "fatContent": "10",
            "invalid": "invalid",
        },
        expected={
            "calories": "100",
            "fatContent": "10",
        },
    ),
    CleanerCase(
        test_id="support `,` seperated numbers instead of `.` (common in Europe)",
        input={
            "calories": "100,000mg",
            "fatContent": "10,000",
        },
        expected={
            "calories": "100.000",
            "fatContent": "10.000",
        },
    ),
    CleanerCase(
        test_id="special support for sodiumContent/cholesterolContent (g -> mg)",
        input={
            "cholesterolContent": "10g",
            "sodiumContent": "10g",
        },
        expected={
            "cholesterolContent": "10000.0",
            "sodiumContent": "10000.0",
        },
    ),
    CleanerCase(
        test_id="special support for sodiumContent/cholesterolContent (mg -> mg)",
        input={
            "cholesterolContent": "10000mg",
            "sodiumContent": "10000mg",
        },
        expected={
            "cholesterolContent": "10000",
            "sodiumContent": "10000",
        },
    ),
    CleanerCase(
        test_id="strip units",
        input={
            "calories": "100 kcal",
        },
        expected={
            "calories": "100",
        },
    ),
    CleanerCase(
        test_id="list as value continues after first value",
        input={
            "calories": ["100 kcal"],
            "sugarContent": "but still tries 555.321",
        },
        expected={
            "sugarContent": "555.321",
        },
    ),
    CleanerCase(
        test_id="multiple decimals",
        input={
            "sodiumContent": "10.1.2g",
        },
        expected={
            "sodiumContent": "10100.0",
        },
    ),
)


@pytest.mark.parametrize("case", nutrition_test_cases, ids=(x.test_id for x in nutrition_test_cases))
def test_cleaner_clean_nutrition(case: CleanerCase):
    result = cleaner.clean_nutrition(case.input)
    assert case.expected == result


@pytest.mark.parametrize(
    "t,max_components,max_decimal_places,expected",
    [
        (timedelta(days=2, seconds=17280), None, 2, "2 days 4 hours 48 minutes"),
        (timedelta(days=2, seconds=17280), 1, 2, "2.2 days"),
        (timedelta(days=365), None, 2, "1 year"),
    ],
)
def test_pretty_print_timedelta(t, max_components, max_decimal_places, expected):
    translator = local_provider()
    assert cleaner.pretty_print_timedelta(t, translator, max_components, max_decimal_places) == expected
