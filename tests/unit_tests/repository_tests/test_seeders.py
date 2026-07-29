from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from mealie.repos.seed.seeders import IngredientFoodsSeeder


def test_food_seeder_deduplicates_by_translated_name(monkeypatch: pytest.MonkeyPatch):
    repos = MagicMock()
    repos.group_id = uuid4()
    seeder = IngredientFoodsSeeder(repos)
    monkeypatch.setattr(seeder, "get_file", lambda _: Path("da-DK.json"))
    monkeypatch.setattr(
        seeder,
        "load_file",
        lambda _: {
            "Sweeteners": {
                "foods": {
                    "sugar": {
                        "name": "sukker",
                        "plural_name": "sukker",
                    }
                }
            }
        },
    )
    monkeypatch.setattr(seeder, "get_all_foods", lambda: [SimpleNamespace(name="sugar")])
    monkeypatch.setattr(seeder, "get_label", lambda _: None)

    foods = list(seeder.load_data("da-DK"))

    assert [food.name for food in foods] == ["sukker"]
