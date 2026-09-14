import importlib
from pathlib import Path

from pydantic import create_model
from pydantic2ts.cli.script import generate_json_schema_v2


def test_type_generation_restores_model_config(monkeypatch) -> None:
    code_generation_dir = Path(__file__).parents[2] / "dev" / "code-generation"
    monkeypatch.syspath_prepend(str(code_generation_dir))
    gen_ts_types = importlib.import_module("gen_ts_types")
    model = create_model("UnconfiguredModel", value=(str, ...))

    with gen_ts_types.forbid_extra_fields([model]):
        assert model.model_config["extra"] == "forbid"
        generate_json_schema_v2([model])

    assert model.model_config == {}
