from uuid import uuid4

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import CreateIngredientFood, CreateIngredientUnit, RecipeIngredient
from mealie.schema.recipe.recipe_notes import RecipeNote
from mealie.schema.recipe.recipe_step import RecipeStep
from mealie.schema.recipe.recipe_translation import (
    IngredientTranslation,
    InstructionTranslation,
    NoteTranslation,
    RecipeTranslation,
)
from mealie.services.recipe.recipe_translation_service import apply_translation, is_translation_stale, source_hash


def _recipe() -> Recipe:
    return Recipe(
        name="Pasta",
        description="A simple pasta dish",
        recipe_yield="2 servings",
        recipe_instructions=[
            RecipeStep(id=uuid4(), text="Boil water."),
            RecipeStep(id=uuid4(), text="Cook pasta."),
        ],
        recipe_ingredient=[
            RecipeIngredient(reference_id=uuid4(), note="200g pasta", quantity=200),
            RecipeIngredient(reference_id=uuid4(), note="salt", quantity=1),
        ],
        notes=[RecipeNote(title="Tip", text="Salt the water.")],
    )


def _full_translation(recipe: Recipe) -> RecipeTranslation:
    return RecipeTranslation(
        locale="es-ES",
        name="Pasta ES",
        description="Un plato de pasta sencillo",
        recipe_yield="2 raciones",
        source_hash=source_hash(recipe),
        instructions=[
            InstructionTranslation(instruction_id=step.id, text=f"ES: {step.text}")
            for step in recipe.recipe_instructions
        ],
        ingredients=[
            IngredientTranslation(ingredient_id=ing.reference_id, note=f"ES: {ing.note}")
            for ing in recipe.recipe_ingredient
        ],
        notes=[NoteTranslation(note_index=0, title="Consejo", text="Sala el agua.")],
    )


def test_apply_translation_substitutes_text_and_keeps_structure():
    recipe = _recipe()
    translated = apply_translation(recipe, _full_translation(recipe))

    assert translated.name == "Pasta ES"
    assert translated.translated_locale == "es-ES"
    assert [s.text for s in translated.recipe_instructions] == ["ES: Boil water.", "ES: Cook pasta."]
    assert [i.note for i in translated.recipe_ingredient] == ["ES: 200g pasta", "ES: salt"]
    assert translated.notes[0].text == "Sala el agua."

    # Structure is untouched
    for orig, trans in zip(recipe.recipe_ingredient, translated.recipe_ingredient, strict=True):
        assert orig.quantity == trans.quantity
        assert orig.reference_id == trans.reference_id
    for orig, trans in zip(recipe.recipe_instructions, translated.recipe_instructions, strict=True):
        assert orig.id == trans.id

    # The original recipe is not mutated
    assert recipe.name == "Pasta"
    assert recipe.recipe_instructions[0].text == "Boil water."


def _recipe_with_food_and_unit() -> Recipe:
    return Recipe(
        name="Salad",
        recipe_ingredient=[
            RecipeIngredient(
                reference_id=uuid4(),
                quantity=1,
                food=CreateIngredientFood(name="cucumber", plural_name="cucumbers"),
                unit=CreateIngredientUnit(name="tablespoon", plural_name="tablespoons"),
                note="large",
            ),
        ],
    )


def test_apply_translation_overlays_food_and_unit_names():
    recipe = _recipe_with_food_and_unit()
    ing = recipe.recipe_ingredient[0]
    translation = RecipeTranslation(
        locale="es-ES",
        ingredients=[
            IngredientTranslation(
                ingredient_id=ing.reference_id,
                note="grande",
                food_name="pepino",
                unit_name="cucharada",
            )
        ],
    )

    translated = apply_translation(recipe, translation)
    tr_ing = translated.recipe_ingredient[0]

    # Food/unit display names are overlaid onto both singular and plural slots
    assert tr_ing.food is not None and tr_ing.unit is not None
    assert tr_ing.food.name == "pepino"
    assert tr_ing.food.plural_name == "pepino"
    assert tr_ing.unit.name == "cucharada"
    assert tr_ing.unit.plural_name == "cucharada"
    assert tr_ing.note == "grande"

    # Structure (quantity, reference id) is untouched
    assert tr_ing.quantity == ing.quantity
    assert tr_ing.reference_id == ing.reference_id

    # The canonical recipe's shared food/unit are not mutated
    assert recipe.recipe_ingredient[0].food.name == "cucumber"
    assert recipe.recipe_ingredient[0].unit.name == "tablespoon"


def test_source_hash_detects_food_and_unit_name_change():
    recipe = _recipe_with_food_and_unit()
    h = source_hash(recipe)

    # Renaming the food invalidates the translation
    recipe_food = recipe.model_copy(deep=True)
    recipe_food.recipe_ingredient[0].food.name = "zucchini"
    assert source_hash(recipe_food) != h

    # Renaming the unit invalidates the translation
    recipe_unit = recipe.model_copy(deep=True)
    recipe_unit.recipe_ingredient[0].unit.name = "teaspoon"
    assert source_hash(recipe_unit) != h


def test_apply_translation_missing_keys_fall_back_to_source():
    recipe = _recipe()
    partial = RecipeTranslation(
        locale="es-ES",
        name="Pasta ES",
        # description omitted -> keep original
        instructions=[InstructionTranslation(instruction_id=recipe.recipe_instructions[0].id, text="ES: Boil water.")],
        # second step, all ingredients, notes omitted -> keep original
    )

    translated = apply_translation(recipe, partial)
    assert translated.name == "Pasta ES"
    assert translated.description == "A simple pasta dish"
    assert translated.recipe_instructions[0].text == "ES: Boil water."
    assert translated.recipe_instructions[1].text == "Cook pasta."
    assert translated.recipe_ingredient[0].note == "200g pasta"


def test_source_hash_stable_and_change_detection():
    recipe = _recipe()
    h = source_hash(recipe)

    # Recomputing over the same content is stable
    assert source_hash(_recipe_like(recipe)) == h

    # Structural-only change (quantity) does not invalidate the translation
    recipe_qty = _recipe_like(recipe)
    recipe_qty.recipe_ingredient[0].quantity = 999
    assert source_hash(recipe_qty) == h

    # Changing translatable text does change the hash
    recipe_text = _recipe_like(recipe)
    recipe_text.description = "A different description"
    assert source_hash(recipe_text) != h

    assert is_translation_stale(recipe_text, h) is True
    assert is_translation_stale(recipe, h) is False


def _recipe_like(recipe: Recipe) -> Recipe:
    """A deep copy with identical ids so hashing is comparable."""
    return recipe.model_copy(deep=True)
