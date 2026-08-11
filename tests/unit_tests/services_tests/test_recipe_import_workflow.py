import json
import re
from pathlib import Path

import pytest

import mealie
from mealie.lang import get_locale_provider
from mealie.lang.providers import TRANSLATIONS
from mealie.services.openai.content import (
    MAX_SOURCE_CONTENT_LENGTH,
    TRUNCATION_NOTICE,
    truncate_source_content,
    truncate_source_parts,
)
from mealie.services.recipe.import_workflow.compilers import DEFAULT_SOURCE_COMPILERS
from mealie.services.recipe.import_workflow.workflow import DEFAULT_WORKFLOW_STEPS

MEALIE_DIR = Path(mealie.__file__).parent
PROGRESS_KEY_PATTERN = re.compile(r"[\"'](recipe\.create-progress\.[a-zA-Z0-9-]+)[\"']")
IMPORT_ERROR_KEY_PATTERN = re.compile(r"[\"'](recipe\.import-errors\.[a-zA-Z0-9-]+)[\"']")

translator = get_locale_provider("en-US")


def is_translatable(key: str) -> bool:
    """The JSON provider falls back to returning the key itself when it can't resolve one."""

    return translator.t(key) != key


def declared_progress_keys() -> list[str]:
    """Progress keys declared by the workflow's steps and source compilers."""

    keys = [step.progress_key for step in DEFAULT_WORKFLOW_STEPS if step.progress_key]
    keys += [compiler.progress_key for compiler in DEFAULT_SOURCE_COMPILERS if compiler.progress_key]
    return keys


def keys_in_source(pattern: re.Pattern) -> list[str]:
    """Every matching translation key referenced as a literal anywhere in the backend."""

    keys: set[str] = set()
    for path in MEALIE_DIR.rglob("*.py"):
        keys.update(pattern.findall(path.read_text()))

    return sorted(keys)


def progress_keys_in_source() -> list[str]:
    return keys_in_source(PROGRESS_KEY_PATTERN)


def import_error_keys_in_source() -> list[str]:
    return keys_in_source(IMPORT_ERROR_KEY_PATTERN)


def test_workflow_declares_keys():
    # guards the tests below against silently passing on an empty list
    assert declared_progress_keys()
    assert progress_keys_in_source()
    assert import_error_keys_in_source()


@pytest.mark.parametrize("key", declared_progress_keys())
def test_declared_progress_keys_are_translatable(key: str):
    assert is_translatable(key), f"Progress key '{key}' is missing from the backend translations"


@pytest.mark.parametrize("key", progress_keys_in_source())
def test_progress_keys_used_in_source_are_translatable(key: str):
    assert is_translatable(key), f"Progress key '{key}' is missing from the backend translations"


@pytest.mark.parametrize("key", import_error_keys_in_source())
def test_import_error_keys_are_translatable(key: str):
    """These are surfaced to the user, so an unresolved key shows up as raw text in the UI."""

    assert is_translatable(key), f"Import error key '{key}' is missing from the backend translations"


def test_short_content_is_not_truncated():
    content = "a" * 100
    assert truncate_source_content(content) == content


def test_content_at_the_limit_is_not_truncated():
    content = "a" * MAX_SOURCE_CONTENT_LENGTH
    assert truncate_source_content(content) == content


def test_long_content_is_truncated_and_marked():
    content = "a" * (MAX_SOURCE_CONTENT_LENGTH + 1)
    truncated = truncate_source_content(content)

    assert truncated.endswith(TRUNCATION_NOTICE)
    assert len(truncated) == MAX_SOURCE_CONTENT_LENGTH + len(TRUNCATION_NOTICE)


def test_content_can_be_truncated_to_a_custom_length():
    assert truncate_source_content("abcdef", max_length=3) == "abc" + TRUNCATION_NOTICE


def test_parts_that_fit_the_budget_are_left_alone():
    parts = ["a" * 10, "b" * 10]
    assert truncate_source_parts(parts, max_length=100) == parts


def test_parts_share_the_budget_evenly_when_all_are_too_long():
    parts = ["a" * 100, "b" * 100]
    assert truncate_source_parts(parts, max_length=10) == ["a" * 5 + TRUNCATION_NOTICE, "b" * 5 + TRUNCATION_NOTICE]


def test_a_short_part_is_not_crowded_out_by_a_long_one():
    """A huge webpage must not swallow the budget and drop the content pasted alongside it."""

    page = "a" * 1000
    pasted = "b" * 10

    truncated_page, truncated_pasted = truncate_source_parts([page, pasted], max_length=100)

    assert truncated_pasted == pasted
    assert truncated_page == "a" * 90 + TRUNCATION_NOTICE


def test_no_parts_is_not_an_error():
    assert truncate_source_parts([]) == []


def test_no_orphaned_import_error_keys():
    """Import error translations that nothing references anymore should be removed."""

    messages = json.loads((TRANSLATIONS / "en-US.json").read_text())
    defined = set(messages["recipe"]["import-errors"])
    used = {key.rsplit(".", 1)[-1] for key in import_error_keys_in_source()}

    assert defined - used == set()


def test_no_orphaned_progress_keys():
    """Progress translations that nothing references anymore should be removed."""

    messages = json.loads((TRANSLATIONS / "en-US.json").read_text())
    defined = set(messages["recipe"]["create-progress"])
    used = {key.rsplit(".", 1)[-1] for key in progress_keys_in_source()}

    assert defined - used == set()
