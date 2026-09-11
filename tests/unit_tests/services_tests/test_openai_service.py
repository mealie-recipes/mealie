import json
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

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


def _make_body(content: str | None, finish_reason: str = "stop") -> str:
    choices = (
        [{"message": {"content": content, "role": "assistant"}, "finish_reason": finish_reason, "index": 0}]
        if content is not None
        else []
    )
    return json.dumps(
        {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 0,
            "model": "test-model",
            "choices": choices,
        }
    )


class _FakeStream:
    def __init__(self, body: str | None, exc: Exception | None = None):
        self._body = body
        self._exc = exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def text(self):
        if self._exc:
            raise self._exc
        return self._body


class _FakeCompletions:
    def __init__(self, *, parse_result=None, parse_exc=None):
        self._parse_result = parse_result
        self._parse_exc = parse_exc
        self.parse_calls: list[dict] = []

    def parse(self, **kwargs):
        self.parse_calls.append(kwargs)
        return _FakeStream(self._parse_result, self._parse_exc)


class _FakeClient:
    def __init__(self, completions: _FakeCompletions):
        self.chat = SimpleNamespace(completions=completions)
        self.chat.completions.with_streaming_response = SimpleNamespace(parse=completions.parse)


@pytest.mark.asyncio
async def test_get_response_sends_schema_as_response_format(settings_stub):
    svc = OpenAIService(_make_mock_repos())
    completions = _FakeCompletions(parse_result=_make_body('{"answer": "hi"}'))
    svc.get_client = MagicMock(return_value=_FakeClient(completions))

    result = await svc.get_response("system prompt", "hello", response_schema=_SampleSchema, provider=_make_provider())

    assert result is not None
    assert result.answer == "hi"
    assert len(completions.parse_calls) == 1
    call = completions.parse_calls[0]
    assert call["response_format"] is _SampleSchema
    assert call["model"] == "test-model"


@pytest.mark.asyncio
async def test_get_response_strips_markdown_fence_from_strict_response(settings_stub):
    svc = OpenAIService(_make_mock_repos())
    completions = _FakeCompletions(parse_result=_make_body('```json\n{"answer": "hi"}\n```'))
    svc.get_client = MagicMock(return_value=_FakeClient(completions))

    result = await svc.get_response("system prompt", "hello", response_schema=_SampleSchema, provider=_make_provider())

    assert result is not None
    assert result.answer == "hi"
    assert len(completions.parse_calls) == 1


@pytest.mark.asyncio
async def test_get_response_returns_none_when_no_choices(settings_stub):
    svc = OpenAIService(_make_mock_repos())
    completions = _FakeCompletions(parse_result=_make_body(None))
    svc.get_client = MagicMock(return_value=_FakeClient(completions))

    result = await svc.get_response("system prompt", "hello", response_schema=_SampleSchema, provider=_make_provider())

    assert result is None


@pytest.mark.asyncio
async def test_get_response_raises_when_response_not_json(settings_stub):
    svc = OpenAIService(_make_mock_repos())
    completions = _FakeCompletions(parse_result=_make_body("still not JSON"))
    svc.get_client = MagicMock(return_value=_FakeClient(completions))

    with pytest.raises(Exception, match="OpenAI Request Failed"):
        await svc.get_response("system prompt", "hello", response_schema=_SampleSchema, provider=_make_provider())


@pytest.mark.asyncio
async def test_get_response_raises_on_length_finish_reason(settings_stub):
    svc = OpenAIService(_make_mock_repos())
    completions = _FakeCompletions(parse_result=_make_body('{"answer": "hi"}', finish_reason="length"))
    svc.get_client = MagicMock(return_value=_FakeClient(completions))

    with pytest.raises(Exception, match="length limit"):
        await svc.get_response("system prompt", "hello", response_schema=_SampleSchema, provider=_make_provider())


@pytest.mark.asyncio
async def test_get_response_raises_on_content_filter_finish_reason(settings_stub):
    svc = OpenAIService(_make_mock_repos())
    completions = _FakeCompletions(parse_result=_make_body('{"answer": "hi"}', finish_reason="content_filter"))
    svc.get_client = MagicMock(return_value=_FakeClient(completions))

    with pytest.raises(Exception, match="content filter"):
        await svc.get_response("system prompt", "hello", response_schema=_SampleSchema, provider=_make_provider())
