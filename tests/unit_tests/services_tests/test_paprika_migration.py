from mealie.services.migrations.paprika import split_paprika_ingredients


def test_split_paprika_ingredients_ignores_blank_lines() -> None:
    assert split_paprika_ingredients("salt\n\npepper\n \n") == ["salt", "pepper"]
