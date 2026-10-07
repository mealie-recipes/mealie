from uuid import uuid4

from mealie.schema.recipe import Recipe
from mealie.services.migrations.utils.fingerprint import recipe_fingerprint


def test_fingerprint_ignores_generated_identity_and_image_paths() -> None:
    first = Recipe(
        name="Cake",
        recipe_ingredient=[{"note": "1 egg", "reference_id": uuid4()}],
        recipe_instructions=[{"text": "Mix gently", "id": uuid4()}],
        image="/tmp/one/image",
    )
    second = Recipe(
        name="Cake",
        recipe_ingredient=[{"note": "1 egg", "reference_id": uuid4()}],
        recipe_instructions=[{"text": "Mix gently", "id": uuid4()}],
        image="/tmp/two/image.jpg",
    )
    assert recipe_fingerprint(first) == recipe_fingerprint(second)


def test_fingerprint_normalizes_whitespace_but_preserves_contents() -> None:
    first = Recipe(name="  Cake  ", recipe_ingredient=[{"note": "1   egg"}])
    second = Recipe(name="Cake", recipe_ingredient=[{"note": "1 egg"}])
    different = Recipe(name="Cake", recipe_ingredient=[{"note": "2 eggs"}])
    assert recipe_fingerprint(first) == recipe_fingerprint(second)
    assert recipe_fingerprint(first) != recipe_fingerprint(different)
