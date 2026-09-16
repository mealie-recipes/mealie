import importlib
import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest
from pydantic import create_model
from pydantic2ts.cli.script import generate_json_schema_v2

CODE_GENERATION_DIR = Path(__file__).parents[2] / "dev" / "code-generation"


@pytest.fixture
def gen_ts_types(monkeypatch: pytest.MonkeyPatch) -> Iterator[ModuleType]:
    """
    Import the code generation script without leaking its top-level `utils` package into
    `sys.modules`, where it could shadow other imports for the rest of the test session
    """
    monkeypatch.syspath_prepend(str(CODE_GENERATION_DIR))
    try:
        yield importlib.import_module("gen_ts_types")
    finally:
        for name in list(sys.modules):
            if name in ("gen_ts_types", "utils") or name.startswith("utils."):
                del sys.modules[name]


def test_type_generation_restores_model_config(gen_ts_types: ModuleType) -> None:
    model = create_model("UnconfiguredModel", value=(str, ...))

    with gen_ts_types.forbid_extra_fields([model]):
        assert model.model_config["extra"] == "forbid"
        generate_json_schema_v2([model])

    assert model.model_config == {}
