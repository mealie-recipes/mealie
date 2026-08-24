from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pydantic
import pytest

import mealie.services.openai.openai as openai_module
from mealie.schema.openai._base import OpenAIBase
from mealie.services.openai.openai import OpenAIService


def _make_mock_repos() -> MagicMock:
    provider_settings = MagicMock()
    provider_settings.ai_enabled = True
    provider_settings.default_provider_id = uuid4()
    provider_settings.audio_provider_id = None
    provider_settings.image_provider_id = None

    repos = MagicMock()
    repos.group_id = uuid4()
    repos.group_ai_provider_settings.get_one.return_value = provider_settings
    repos.group_ai_providers.get_one.return_value = MagicMock()
    return repos


class _SettingsStub:
    OPENAI_CUSTOM_PROMPT_DIR: str | None = None


@pytest.fixture()
def settings_stub(tmp_path, monkeypatch):
    s = _SettingsStub()

    prompts_dir = tmp_path / "prompts"
    (prompts_dir / "recipes").mkdir(parents=True)
    default_prompt = prompts_dir / "recipes" / "parse-recipe-ingredients.txt"
    default_prompt.write_text("DEFAULT PROMPT")

    monkeypatch.setattr(OpenAIService, "PROMPTS_DIR", prompts_dir)

    def _fake_get_app_settings():
        return s

    monkeypatch.setattr(openai_module, "get_app_settings", _fake_get_app_settings)
    return s


def test_get_prompt_default_only(settings_stub):
    svc = OpenAIService(_make_mock_repos())
    out = svc.get_prompt("recipes.parse-recipe-ingredients")
    assert out == "DEFAULT PROMPT"


def test_get_prompt_custom_dir_used(settings_stub, tmp_path):
    custom_dir = tmp_path / "custom"
    (custom_dir / "recipes").mkdir(parents=True)
    (custom_dir / "recipes" / "parse-recipe-ingredients.txt").write_text("CUSTOM PROMPT")

    settings_stub.OPENAI_CUSTOM_PROMPT_DIR = str(custom_dir)

    svc = OpenAIService(_make_mock_repos())
    out = svc.get_prompt("recipes.parse-recipe-ingredients")
    assert out == "CUSTOM PROMPT"


def test_get_prompt_custom_empty_falls_back_to_default(settings_stub, tmp_path):
    custom_dir = tmp_path / "custom"
    (custom_dir / "recipes").mkdir(parents=True)
    (custom_dir / "recipes" / "parse-recipe-ingredients.txt").write_text("")

    settings_stub.OPENAI_CUSTOM_PROMPT_DIR = str(custom_dir)
    svc = OpenAIService(_make_mock_repos())
    out = svc.get_prompt("recipes.parse-recipe-ingredients")
    assert out == "DEFAULT PROMPT"


def test_get_prompt_raises_when_no_files(settings_stub, monkeypatch):
    # Point PROMPTS_DIR to an empty temp folder (already done in fixture) but remove default file
    prompts_dir = OpenAIService.PROMPTS_DIR
    for p in prompts_dir.rglob("*.txt"):
        p.unlink()

    svc = OpenAIService(_make_mock_repos())
    with pytest.raises(OSError) as ei:
        svc.get_prompt("recipes.parse-recipe-ingredients")
    assert "Unable to load prompt" in str(ei.value)


class _SampleSchema(OpenAIBase):
    answer: str


def _make_provider() -> MagicMock:
    provider = MagicMock()
    provider.name = "test-provider"
    provider.model = "test-model"
    return provider


def _make_response(content: str | None) -> SimpleNamespace:
    choices = [SimpleNamespace(message=SimpleNamespace(content=content))] if content is not None else []
    return SimpleNamespace(choices=choices)


def _make_schema_validation_error() -> pydantic.ValidationError:
    try:
        _SampleSchema.model_validate_json("this is plain prose, not JSON")
    except pydantic.ValidationError as e:
        return e
    raise AssertionError("expected model_validate_json to raise")


class _FakeCompletions:
    def __init__(self, *, parse_result=None, parse_exc=None, create_result=None):
        self._parse_result = parse_result
        self._parse_exc = parse_exc
        self._create_result = create_result
        self.create_calls: list[dict] = []

    async def parse(self, **kwargs):
        if self._parse_exc:
            raise self._parse_exc
        return self._parse_result

    async def create(self, **kwargs):
        self.create_calls.append(kwargs)
        return self._create_result


class _FakeClient:
    def __init__(self, completions: _FakeCompletions):
        self.chat = SimpleNamespace(completions=completions)


@pytest.mark.asyncio
async def test_get_response_uses_strict_parse_when_supported(settings_stub):
    svc = OpenAIService(_make_mock_repos())
    completions = _FakeCompletions(parse_result=_make_response('{"answer": "hi"}'))
    svc.get_client = MagicMock(return_value=_FakeClient(completions))

    result = await svc.get_response("system prompt", "hello", response_schema=_SampleSchema, provider=_make_provider())

    assert result is not None
    assert result.answer == "hi"
    assert completions.create_calls == []


@pytest.mark.asyncio
async def test_get_response_falls_back_to_json_object_when_schema_ignored(settings_stub):
    svc = OpenAIService(_make_mock_repos())
    completions = _FakeCompletions(
        parse_exc=_make_schema_validation_error(),
        create_result=_make_response('{"answer": "hi"}'),
    )
    svc.get_client = MagicMock(return_value=_FakeClient(completions))

    result = await svc.get_response("system prompt", "hello", response_schema=_SampleSchema, provider=_make_provider())

    assert result is not None
    assert result.answer == "hi"
    assert len(completions.create_calls) == 1
    assert completions.create_calls[0]["response_format"] == {"type": "json_object"}


@pytest.mark.asyncio
async def test_get_response_raises_when_fallback_also_fails(settings_stub):
    svc = OpenAIService(_make_mock_repos())
    completions = _FakeCompletions(
        parse_exc=_make_schema_validation_error(),
        create_result=_make_response("still not JSON"),
    )
    svc.get_client = MagicMock(return_value=_FakeClient(completions))

    with pytest.raises(Exception, match="OpenAI Request Failed"):
        await svc.get_response("system prompt", "hello", response_schema=_SampleSchema, provider=_make_provider())

    # confirms the fallback was actually attempted, not just the initial strict-mode failure surfacing
    assert len(completions.create_calls) == 1
