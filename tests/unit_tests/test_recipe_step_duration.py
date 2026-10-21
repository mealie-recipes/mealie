"""DB-free duration contracts; run with pytest --noconftest (no app/DB startup)."""

import json
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import Integer
from sqlalchemy.orm import Session

from mealie.db.models import _all_models  # noqa: F401 - register ORM relationships without DB startup
from mealie.db.models.recipe.instruction import RecipeInstruction
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe_step import RecipeStep


@pytest.mark.parametrize("value", [None])
def test_blank_duration_is_unspecified(value):
    step = RecipeStep(text="Rest", durationSeconds=value)
    assert step.duration_seconds is None
    assert step.model_dump(by_alias=True)["durationSeconds"] is None


def test_legacy_step_is_not_assigned_a_time():
    step = RecipeStep(text="Bake for a while")
    assert step.duration_seconds is None
    assert step.text == "Bake for a while"


@pytest.mark.parametrize("seconds", [1, 90, 3661, 172801, 2147483647])
def test_exact_duration_survives_model_and_recipe_json(seconds):
    step = RecipeStep(text="Rest", durationSeconds=seconds)
    # Exercise the existing create mapping, without connecting or writing to a DB.
    with Session() as session:
        mapped = RecipeInstruction(session=session, **step.model_dump())
        mapped.id = uuid4()
        restored = RecipeStep.model_validate(mapped)
    recipe = Recipe(name="Duration fixture", recipeInstructions=[restored])
    payload = json.loads(recipe.model_dump_json(by_alias=True))
    assert payload["recipeInstructions"][0]["durationSeconds"] == seconds
    assert Recipe.model_validate(payload).recipe_instructions[0].duration_seconds == seconds


@pytest.mark.parametrize("number", ["1", "1.0", "1e0", "2147483647.0"])
def test_whole_numeric_json_spellings_are_equivalent(number):
    step = RecipeStep.model_validate_json('{"text":"Rest","durationSeconds":' + number + "}")
    assert type(step.duration_seconds) is int
    assert step.duration_seconds == int(float(number))


@pytest.mark.parametrize(
    "value",
    [
        True,
        False,
        -1,
        1.5,
        0.5,
        2147483647.5,
        float("inf"),
        float("-inf"),
        float("nan"),
        "PT1M",
        "90",
        "0",
        "",
        " ",
        2147483648,
        2147483648.0,
        1e30,
    ],
)
def test_duration_rejects_lossy_or_out_of_range_input(value):
    with pytest.raises(ValidationError):
        RecipeStep(text="Rest", durationSeconds=value)


def test_duration_column_is_nullable_without_a_zero_default():
    column = RecipeInstruction.__table__.c.duration_seconds
    assert isinstance(column.type, Integer)
    assert column.nullable
    assert column.default is None
    assert column.server_default is None


@pytest.mark.parametrize("dialect", ["sqlite", "postgresql"])
def test_additive_migration_sql_without_database(dialect):
    from importlib.util import module_from_spec, spec_from_file_location
    from io import StringIO
    from pathlib import Path

    from alembic.migration import MigrationContext
    from alembic.operations import Operations

    path = (
        Path(__file__).parents[2]
        / "mealie/alembic/versions/2026-10-21-00.00.00_afdc42353aa4_add_duration_to_recipe_steps.py"
    )
    spec = spec_from_file_location("step_duration_migration", path)
    migration = module_from_spec(spec)
    spec.loader.exec_module(migration)
    assert migration.down_revision == "a91720b8a7e7"
    output = StringIO()
    context = MigrationContext.configure(dialect_name=dialect, opts={"as_sql": True, "output_buffer": output})
    with Operations.context(context):
        migration.upgrade()
    sql = output.getvalue().upper()
    assert "ALTER TABLE RECIPE_INSTRUCTIONS ADD COLUMN DURATION_SECONDS INTEGER" in sql
    assert "NOT NULL" not in sql
    assert "DEFAULT" not in sql
    assert "UPDATE " not in sql


def test_raw_json_export_preserves_exact_duration(tmp_path):
    from mealie.services.recipe.template_service import TemplateService

    recipe = Recipe(name="Timed steps", recipeInstructions=[{"text": "Rest", "durationSeconds": 3661}])
    path = TemplateService(temp=tmp_path).render(recipe, "raw")
    payload = json.loads(path.read_text())
    assert payload["recipeInstructions"][0]["durationSeconds"] == 3661


def test_existing_instruction_update_and_clear_without_database():
    from unittest.mock import Mock

    from mealie.db.models._model_utils.auto_init import handle_one_to_many_list

    with Session() as unbound:
        instruction = RecipeInstruction(session=unbound, text="Rest", duration_seconds=3661)
        instruction.id = uuid4()
    session = Mock()
    session.execute.return_value.scalars.return_value.one_or_none.return_value = instruction
    for value in (42, None):
        step = RecipeStep(id=instruction.id, text="Rest", duration_seconds=value)
        updated = handle_one_to_many_list(session, "id", RecipeInstruction, [step.model_dump()])
        assert updated == [instruction]
        assert RecipeStep.model_validate(instruction).duration_seconds == value
        assert instruction.text == "Rest"


def test_api_schema_documents_optional_integer_seconds():
    schema = RecipeStep.model_json_schema(by_alias=True)
    duration = schema["properties"]["durationSeconds"]
    assert "durationSeconds" not in schema["required"]
    assert duration["default"] is None
    assert duration["anyOf"] == [
        {"maximum": 2147483647, "minimum": 1, "type": "integer"},
        {"type": "null"},
    ]


def test_edit_and_clear_duration_preserve_step_text():
    step = RecipeStep(text="Rest", durationSeconds=3661)
    edited = RecipeStep.model_validate({**step.model_dump(), "duration_seconds": 42})
    cleared = RecipeStep.model_validate({**edited.model_dump(), "duration_seconds": None})
    assert edited.duration_seconds == 42
    assert cleared.duration_seconds is None
    assert cleared.text == "Rest"


@pytest.mark.parametrize("value", [0, 0.0, None])
def test_zero_is_unspecified(value):
    assert RecipeStep(durationSeconds=value, text="Rest").duration_seconds is None
