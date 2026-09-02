from uuid import uuid4

import pytest
from pydantic import ValidationError

from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    IngredientFoodSummary,
    RecipeIngredient,
    SubstitutionBase,
)
from tests.utils.factories import random_string


def test_substitution_accepts_all_three_forms():
    """A substitution may be a food, a note, or a food with a note attached."""

    food_id = uuid4()
    food = CreateIngredientFood(
        name=random_string(),
        substitutions=[
            {"substituteFoodId": str(food_id)},
            {"note": "water and a bouillon cube"},
            {"substituteFoodId": str(uuid4()), "note": "1 tbsp vinegar per cup"},
        ],
    )

    assert len(food.substitutions) == 3
    assert food.substitutions[0].substitute_food_id == food_id
    assert food.substitutions[0].note is None
    assert food.substitutions[1].substitute_food_id is None
    assert food.substitutions[1].note == "water and a bouillon cube"
    assert food.substitutions[2].substitute_food_id is not None
    assert food.substitutions[2].note == "1 tbsp vinegar per cup"


def test_substitution_rejects_empty_edge_directly():
    with pytest.raises(ValidationError):
        SubstitutionBase(substitute_food_id=None, note=None)


@pytest.mark.parametrize("note", [None, "", "   ", "\n\t "])
def test_empty_substitutions_are_pruned_not_rejected(note):
    """
    An empty row is a UI artifact rather than a client bug, so the parent drops it. A
    whitespace-only note counts as absent.
    """

    food = CreateIngredientFood(name=random_string(), substitutions=[{"note": note}])
    assert food.substitutions == []


def test_blank_note_is_normalized_to_none_alongside_a_food():
    food_id = uuid4()
    food = CreateIngredientFood(name=random_string(), substitutions=[{"substituteFoodId": str(food_id), "note": "   "}])

    assert len(food.substitutions) == 1
    assert food.substitutions[0].substitute_food_id == food_id
    assert food.substitutions[0].note is None


def test_note_is_stripped():
    food = CreateIngredientFood(name=random_string(), substitutions=[{"note": "  half butter half applesauce  "}])
    assert food.substitutions[0].note == "half butter half applesauce"


def test_duplicate_substitute_foods_are_collapsed_keeping_the_first():
    food_id = uuid4()
    other_id = uuid4()
    food = CreateIngredientFood(
        name=random_string(),
        substitutions=[
            {"substituteFoodId": str(food_id), "note": "first"},
            {"substituteFoodId": str(food_id), "note": "second"},
            {"substituteFoodId": str(other_id)},
        ],
    )

    assert [sub.substitute_food_id for sub in food.substitutions] == [food_id, other_id]
    assert food.substitutions[0].note == "first"


def test_note_only_substitutions_are_never_collapsed():
    """
    Two textual workarounds are two legitimate rows. A set-based dedupe that doesn't skip
    nulls silently loses all but one of them.
    """

    food = CreateIngredientFood(
        name=random_string(),
        substitutions=[
            {"note": "water and a bouillon cube"},
            {"note": "half butter half applesauce"},
            {"note": "whatever hard cheese you have"},
        ],
    )

    assert len(food.substitutions) == 3


def test_identical_note_only_substitutions_are_kept():
    food = CreateIngredientFood(
        name=random_string(),
        substitutions=[{"note": "a splash of vinegar"}, {"note": "a splash of vinegar"}],
    )

    assert len(food.substitutions) == 2


def test_self_substitution_is_rejected():
    food_id = uuid4()
    with pytest.raises(ValidationError):
        CreateIngredientFood(id=food_id, name=random_string(), substitutions=[{"substituteFoodId": str(food_id)}])


def test_self_substitution_check_ignores_other_foods():
    food_id = uuid4()
    food = CreateIngredientFood(id=food_id, name=random_string(), substitutions=[{"substituteFoodId": str(uuid4())}])

    assert len(food.substitutions) == 1


def test_ingredient_food_summary_does_not_recurse():
    """
    The summary exists so an edge can reference a food without Pydantic walking
    food -> substitutions -> food forever.
    """

    summary = IngredientFoodSummary(id=uuid4(), name=random_string(), plural_name=random_string())
    dumped = summary.model_dump(by_alias=True)

    assert set(dumped) == {"id", "name", "pluralName"}


def test_recipe_ingredient_substitutions_are_pruned_and_deduped():
    food_id = uuid4()
    ingredient = RecipeIngredient(
        note="",
        substitutions=[
            {"substituteFoodId": str(food_id)},
            {"substituteFoodId": str(food_id), "note": "dupe"},
            {"note": "   "},
            {"note": "pork works"},
        ],
    )

    assert len(ingredient.substitutions) == 2
    assert ingredient.substitutions[0].substitute_food_id == food_id
    assert ingredient.substitutions[1].note == "pork works"


def test_recipe_ingredient_defaults_to_no_substitutions():
    assert RecipeIngredient(note=random_string()).substitutions == []
