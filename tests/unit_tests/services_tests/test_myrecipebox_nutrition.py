from typing import Any
from unittest.mock import Mock
import pytest
from mealie.services.migrations.myrecipebox import MyRecipeBoxMigrator
from mealie.services.scraper import cleaner

@pytest.fixture
def nutrition_parser() -> MyRecipeBoxMigrator:
    # Evita o construtor, que consulta o banco.
    return MyRecipeBoxMigrator.__new__(MyRecipeBoxMigrator)

@pytest.fixture
def nutrition_cleaner(monkeypatch: pytest.MonkeyPatch) -> Mock:
    dependency = Mock(side_effect=lambda nutrition: dict(nutrition))
    monkeypatch.setattr(cleaner, "clean_nutrition", dependency)
    return dependency

@pytest.mark.parametrize(
    ("input_", "expected"),
    [
        pytest.param(None, None, id="CT01-absent-input"),
        pytest.param("", None, id="CT02-empty-string"),
        pytest.param(1, None, id="CT03-non-string-input"),
        pytest.param("protein:1", {"proteinContent": "1"}, id="CT04-valid-pair"),
        pytest.param(":1", None, id="CT05-empty-key"),
        pytest.param("protein:", None, id="CT06-empty-value"),
        pytest.param(":", None, id="CT07-both-parts-empty"),
        pytest.param("invalid", None, id="CT08-missing-separator"),
        pytest.param(" \t:1", None, id="CT09-whitespace-key"),
        pytest.param("protein: \t", None, id="CT10-whitespace-value"),
        pytest.param("\n", None, id="CT11-only-empty-lines"),
        pytest.param(
            "\ninvalid\nprotein:10\n   \nfat:2\n",
            {"proteinContent": "10", "fatContent": "2"},
            id="CT12-valid-and-invalid-lines",
        ),
        pytest.param("  PrOtEiN : 0  ", {"proteinContent": "0"}, id="CT13-case-spaces-zero"),
        pytest.param("a:1", {"a": "1"}, id="CT14-minimal-pair-unknown-key"),
        pytest.param("custom:10:20", {"custom": "10:20"}, id="CT15-additional-colon"),
        pytest.param("protein:10\nprotein:20", {"proteinContent": "20"}, id="CT16-duplicate-key"),
        pytest.param(
            "carbohydrate:1\nprotein:2\nfat:3\nsaturatedfat:4\ntransfat:5\n"
            "sodium:6\nfiber:7\nsugar:8\nunsaturatedfat:9",
            {
                "carbohydrateContent": "1",
                "proteinContent": "2",
                "fatContent": "3",
                "saturatedFatContent": "4",
                "transFatContent": "5",
                "sodiumContent": "6",
                "fiberContent": "7",
                "sugarContent": "8",
                "unsaturatedFatContent": "9",
            },
            id="CT17-all-supported-aliases",
        ),
    ],
)
def test_parse_nutrition(
    nutrition_parser: MyRecipeBoxMigrator, nutrition_cleaner: Mock, input_: Any, expected: dict[str, str] | None
) -> None:
    assert nutrition_parser.parse_nutrition(input_) == expected
    if expected is None:
        nutrition_cleaner.assert_not_called()
    else:
        nutrition_cleaner.assert_called_once_with(expected)


def test_CT18_cleaner_delegation(nutrition_parser: MyRecipeBoxMigrator, nutrition_cleaner: Mock) -> None:
    normalized = {"proteinContent": "10"}
    nutrition_cleaner.side_effect = None
    nutrition_cleaner.return_value = normalized

    result = nutrition_parser.parse_nutrition("protein: 10 g")

    nutrition_cleaner.assert_called_once_with({"proteinContent": "10 g"})
    assert result is normalized
