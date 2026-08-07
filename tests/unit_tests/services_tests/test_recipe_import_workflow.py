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
)
from mealie.services.recipe.import_workflow.compilers import DEFAULT_SOURCE_COMPILERS
from mealie.services.recipe.import_workflow.workflow import DEFAULT_WORKFLOW_STEPS

MEALIE_DIR = Path(mealie.__file__).parent
PROGRESS_KEY_PATTERN = re.compile(r"[\"'](recipe\.create-progress\.[a-zA-Z0-9-]+)[\"']")

translator = get_locale_provider("en-US")


def is_translatable(key: str) -> bool:
    """The JSON provider falls back to returning the key itself when it can't resolve one."""

    return translator.t(key) != key


def declared_progress_keys() -> list[str]:
    """Progress keys declared by the workflow's steps and source compilers."""

    keys = [step.progress_key for step in DEFAULT_WORKFLOW_STEPS if step.progress_key]
    keys += [compiler.progress_key for compiler in DEFAULT_SOURCE_COMPILERS if compiler.progress_key]
    return keys


def progress_keys_in_source() -> list[str]:
    """Every progress key referenced as a literal anywhere in the backend."""

    keys: set[str] = set()
    for path in MEALIE_DIR.rglob("*.py"):
        keys.update(PROGRESS_KEY_PATTERN.findall(path.read_text()))

    return sorted(keys)


def test_workflow_declares_progress_keys():
    # guards the tests below against silently passing on an empty list
    assert declared_progress_keys()
    assert progress_keys_in_source()


@pytest.mark.parametrize("key", declared_progress_keys())
def test_declared_progress_keys_are_translatable(key: str):
    assert is_translatable(key), f"Progress key '{key}' is missing from the backend translations"


@pytest.mark.parametrize("key", progress_keys_in_source())
def test_progress_keys_used_in_source_are_translatable(key: str):
    assert is_translatable(key), f"Progress key '{key}' is missing from the backend translations"


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


def test_no_orphaned_progress_keys():
    """Progress translations that nothing references anymore should be removed."""

    messages = json.loads((TRANSLATIONS / "en-US.json").read_text())
    defined = set(messages["recipe"]["create-progress"])
    used = {key.rsplit(".", 1)[-1] for key in progress_keys_in_source()}

    assert defined - used == set()
