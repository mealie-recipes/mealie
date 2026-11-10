import io
import json
import wave
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import httpx
import openai
import pytest

from mealie.schema.group.ai_providers import AIPromptMode, AIPromptOverrideOut, AIProviderOut
from mealie.schema.openai._base import OpenAIBase
from mealie.services.openai.openai import GLOBAL_PROMPT_NAME, OpenAIDataInjection, OpenAIService


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


@pytest.fixture()
def settings_stub(tmp_path, monkeypatch):
    prompts_dir = tmp_path / "prompts"
    (prompts_dir / "recipes").mkdir(parents=True)
    default_prompt = prompts_dir / "recipes" / "parse-recipe-ingredients.txt"
    default_prompt.write_text("DEFAULT PROMPT")

    monkeypatch.setattr(OpenAIService, "PROMPTS_DIR", prompts_dir)
    return prompts_dir


def test_get_prompt_default_only(settings_stub):
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


def _make_override(name: str, mode: AIPromptMode, content: str) -> AIPromptOverrideOut:
    return AIPromptOverrideOut(id=uuid4(), name=name, mode=mode, content=content)


def _make_repos_with_overrides(*overrides: AIPromptOverrideOut) -> MagicMock:
    repos = _make_mock_repos()
    repos.group_ai_prompt_overrides.get_all.return_value = list(overrides)
    return repos


def test_get_prompt_append_adds_instructions_after_default(settings_stub):
    repos = _make_repos_with_overrides(
        _make_override("recipes.parse-recipe-ingredients", AIPromptMode.append, "EXTRA"),
    )
    out = OpenAIService(repos).get_prompt("recipes.parse-recipe-ingredients")

    assert out.startswith("DEFAULT PROMPT\n")
    assert out.endswith("\nEXTRA")
    assert "take priority" in out


def test_get_prompt_override_replaces_default(settings_stub):
    repos = _make_repos_with_overrides(
        _make_override("recipes.parse-recipe-ingredients", AIPromptMode.override, "OVERRIDE"),
    )
    out = OpenAIService(repos).get_prompt("recipes.parse-recipe-ingredients")
    assert out == "OVERRIDE"


def test_get_prompt_ignores_other_prompts_overrides(settings_stub):
    repos = _make_repos_with_overrides(
        _make_override("recipes.build-recipe", AIPromptMode.override, "OVERRIDE"),
    )
    out = OpenAIService(repos).get_prompt("recipes.parse-recipe-ingredients")
    assert out == "DEFAULT PROMPT"


def test_get_prompt_global_instructions_come_before_prompt_instructions(settings_stub):
    repos = _make_repos_with_overrides(
        _make_override("recipes.parse-recipe-ingredients", AIPromptMode.append, "PROMPT EXTRA"),
        _make_override(GLOBAL_PROMPT_NAME, AIPromptMode.append, "GLOBAL EXTRA"),
    )
    out = OpenAIService(repos).get_prompt("recipes.parse-recipe-ingredients")

    assert out.startswith("DEFAULT PROMPT\n")
    assert out.endswith("GLOBAL EXTRA\n\nPROMPT EXTRA")


def test_get_prompt_global_instructions_apply_to_overridden_prompt(settings_stub):
    repos = _make_repos_with_overrides(
        _make_override("recipes.parse-recipe-ingredients", AIPromptMode.override, "OVERRIDE"),
        _make_override(GLOBAL_PROMPT_NAME, AIPromptMode.append, "GLOBAL EXTRA"),
    )
    out = OpenAIService(repos).get_prompt("recipes.parse-recipe-ingredients")

    assert out.startswith("OVERRIDE\n")
    assert out.endswith("\nGLOBAL EXTRA")
    assert "DEFAULT PROMPT" not in out


def test_get_prompt_data_injections_come_after_instructions(settings_stub):
    repos = _make_repos_with_overrides(
        _make_override("recipes.parse-recipe-ingredients", AIPromptMode.override, "OVERRIDE"),
        _make_override(GLOBAL_PROMPT_NAME, AIPromptMode.append, "GLOBAL EXTRA"),
    )
    out = OpenAIService(repos).get_prompt(
        "recipes.parse-recipe-ingredients",
        data_injections=[OpenAIDataInjection(description="Units", value="cup")],
    )

    assert out.index("OVERRIDE") < out.index("GLOBAL EXTRA") < out.index("Units") < out.index("cup")


def test_get_prompt_system_prompt_skips_global_instructions(settings_stub):
    (OpenAIService.PROMPTS_DIR / "system").mkdir()
    (OpenAIService.PROMPTS_DIR / "system" / "compile-source.txt").write_text("SYSTEM PROMPT")
    repos = _make_repos_with_overrides(
        _make_override("system.compile-source", AIPromptMode.append, "PROMPT EXTRA"),
        _make_override(GLOBAL_PROMPT_NAME, AIPromptMode.append, "GLOBAL EXTRA"),
    )
    out = OpenAIService(repos).get_prompt("system.compile-source")

    assert out.startswith("SYSTEM PROMPT\n")
    assert out.endswith("\nPROMPT EXTRA")
    assert "GLOBAL EXTRA" not in out


def test_get_prompt_without_group_skips_overrides(settings_stub):
    repos = _make_repos_with_overrides(
        _make_override(GLOBAL_PROMPT_NAME, AIPromptMode.append, "GLOBAL EXTRA"),
    )
    repos.group_id = None
    out = OpenAIService(repos).get_prompt("recipes.parse-recipe-ingredients")

    assert out == "DEFAULT PROMPT"
    repos.group_ai_prompt_overrides.get_all.assert_not_called()


def _make_test_provider() -> AIProviderOut:
    return AIProviderOut(
        id=uuid4(),
        name="Test Provider",
        base_url="https://example.com/v1",
        api_key="sk-test",
        model="gpt-test",
        timeout=300,
        request_headers={},
        request_params={},
    )


class _FakeOpenAIText:
    def __init__(self, text: str):
        self.text = text


def _patch_ping(monkeypatch, *, text_response="Hello!", image_response: str | None = "unused", image_error=None):
    """
    Stubs OpenAIService.ping() so test_connection's two calls (text, then image) can be driven
    independently without going through the real OpenAI client.

    - text_response: what the plain-text ping returns (a falsy value simulates no response)
    - image_response: what the image ping returns; ignored if image_error is set
    - image_error: if set, the image ping raises this instead of returning
    """

    async def _fake_ping(self, provider, message, images=None):
        if images:
            if image_error:
                raise image_error
            return _FakeOpenAIText(image_response) if image_response else None
        return _FakeOpenAIText(text_response) if text_response else None

    monkeypatch.setattr(OpenAIService, "ping", _fake_ping)


@pytest.mark.asyncio
async def test_ping_uses_debug_prompt_and_delegates_to_get_response(settings_stub, monkeypatch):
    captured = {}

    async def _fake_get_response(self, prompt, message, *, response_schema, attachments=None, provider=None):
        captured.update(prompt=prompt, message=message, attachments=attachments, provider=provider)
        return _FakeOpenAIText("ok")

    monkeypatch.setattr(OpenAIService, "get_response", _fake_get_response)

    svc = OpenAIService(_make_mock_repos())
    provider = _make_test_provider()
    result = await svc.ping(provider, "hello there", images=["fake-image"])

    assert result.text == "ok"
    assert captured == {
        "prompt": (OpenAIService.TESTING_DIR / "debug.txt").read_text(),
        "message": "hello there",
        "attachments": ["fake-image"],
        "provider": provider,
    }


@pytest.mark.asyncio
async def test_connection_success_recognizes_test_image(settings_stub, monkeypatch):
    # The bundled test image is a screenshot of a "Tomato & Egg Stir-Fry" recipe - a reply that
    # actually read it will contain the recipe's keywords.
    _patch_ping(monkeypatch, image_response="Tomato & Egg Stir-Fry")

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is True
    assert result.message is None
    assert result.supports_images is True


@pytest.mark.asyncio
async def test_connection_success_but_image_reply_does_not_mention_recipe(settings_stub, monkeypatch):
    # Some providers accept an image parameter without erroring but don't actually look at it.
    # That's reported as "no image support", not as a failed connection.
    _patch_ping(monkeypatch, image_response="I'm not sure what you mean, could you clarify?")

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is True
    assert result.supports_images is False


@pytest.mark.asyncio
async def test_connection_success_but_image_request_errors(settings_stub, monkeypatch):
    # e.g. a text-only model that rejects an image_url content part outright - still a working
    # provider, just not one that can be used as the image provider.
    _patch_ping(monkeypatch, image_error=Exception("model does not support image input"))

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is True
    assert result.supports_images is False


@pytest.mark.asyncio
async def test_connection_text_failure_never_attempts_image_check(settings_stub, monkeypatch):
    calls: list[list | None] = []

    async def _fake_ping(self, provider, message, images=None):
        calls.append(images)
        raise Exception("connection refused")

    monkeypatch.setattr(OpenAIService, "ping", _fake_ping)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is False
    assert result.supports_images is None
    assert calls == [None]  # only the text ping ran


@pytest.mark.asyncio
async def test_connection_empty_response_is_a_failure(settings_stub, monkeypatch):
    _patch_ping(monkeypatch, text_response=None)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is False
    assert result.message == "No response received from the provider."
    assert result.supports_images is None


@pytest.mark.asyncio
async def test_connection_failure_never_returns_the_providers_response_body(settings_stub, monkeypatch):
    """
    This route is open to group managers, not just admins, so a manager could point base_url at an
    internal host. The result must identify the error without relaying anything that host returned.
    """
    response = httpx.Response(
        status_code=404,
        request=httpx.Request("POST", "https://internal-host.local/v1/chat/completions"),
        content=b"<html>internal service page, top secret</html>",
    )
    sdk_error = openai.NotFoundError(
        message="Error code: 404 - {'error': {'message': 'super secret internal detail'}}",
        response=response,
        body={"error": {"message": "super secret internal detail"}},
    )

    async def _fake_ping(self, provider, message, images=None):
        try:
            raise sdk_error
        except Exception as e:
            # Mirrors get_response()'s own wrapping (`raise Exception(...) from e`)
            raise Exception(f"OpenAI Request Failed. {e.__class__.__name__}: {e}") from e

    monkeypatch.setattr(OpenAIService, "ping", _fake_ping)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is False
    assert result.message == "NotFoundError (HTTP 404)"
    assert "secret" not in result.message


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
async def test_get_response_ignores_unknown_service_tier(settings_stub):
    # Groq returns "on_demand", which isn't one of the OpenAI SDK's service tiers
    body = json.loads(_make_body('{"answer": "hi"}'))
    body["service_tier"] = "on_demand"
    svc = OpenAIService(_make_mock_repos())
    completions = _FakeCompletions(parse_result=json.dumps(body))
    svc.get_client = MagicMock(return_value=_FakeClient(completions))

    result = await svc.get_response("system prompt", "hello", response_schema=_SampleSchema, provider=_make_provider())

    assert result is not None
    assert result.answer == "hi"


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


class _FakeTranscriptions:
    def __init__(self, error: Exception | None = None):
        self.error = error
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return SimpleNamespace(text="")


def _patch_transcription(monkeypatch, *, error: Exception | None = None) -> _FakeTranscriptions:
    """Stubs get_client() so the transcription leg of test_connection never reaches a real provider."""
    transcriptions = _FakeTranscriptions(error)
    client = SimpleNamespace(audio=SimpleNamespace(transcriptions=transcriptions))
    monkeypatch.setattr(OpenAIService, "get_client", lambda self, provider: client)
    return transcriptions


def _make_audio_only_service(provider: AIProviderOut) -> OpenAIService:
    repos = _make_mock_repos()
    repos.group_ai_provider_settings.get_one.return_value.audio_provider_id = provider.id
    return OpenAIService(repos)


@pytest.mark.asyncio
async def test_connection_audio_only_provider_passes_on_transcription(settings_stub, monkeypatch):
    # A transcription-only model can't answer the chat ping, so an audio-only provider is tested by
    # transcribing a moment of silence first (#8577). The chat ping is set up to fail, so a success
    # here can only come from the transcription.
    transcriptions = _patch_transcription(monkeypatch)
    _patch_ping(monkeypatch, text_response=None)

    provider = _make_test_provider()
    result = await _make_audio_only_service(provider).test_connection(provider)

    assert result.success is True
    assert result.supports_images is None
    assert len(transcriptions.calls) == 1
    assert transcriptions.calls[0]["model"] == provider.model
    filename, audio, content_type = transcriptions.calls[0]["file"]
    assert (filename, content_type) == ("connection-test.wav", "audio/wav")
    with wave.open(io.BytesIO(audio)) as wav:
        assert wav.getnframes() > 0


@pytest.mark.asyncio
async def test_connection_audio_only_provider_falls_back_to_chat(settings_stub, monkeypatch):
    # Some audio providers are chat models that take audio input, and an import falls back to chat
    # for them. The test does the same, so they still pass.
    transcriptions = _patch_transcription(monkeypatch, error=RuntimeError("no transcription endpoint"))
    _patch_ping(monkeypatch, image_response="Tomato & Egg Stir-Fry")

    provider = _make_test_provider()
    result = await _make_audio_only_service(provider).test_connection(provider)

    assert result.success is True
    assert len(transcriptions.calls) == 1


@pytest.mark.asyncio
async def test_connection_audio_only_provider_fails_when_neither_works(settings_stub, monkeypatch):
    _patch_transcription(monkeypatch, error=RuntimeError("bad key"))
    _patch_ping(monkeypatch, text_response=None)

    provider = _make_test_provider()
    result = await _make_audio_only_service(provider).test_connection(provider)

    assert result.success is False


@pytest.mark.parametrize("other_role", ["default_provider_id", "image_provider_id"])
@pytest.mark.asyncio
async def test_connection_skips_transcription_when_provider_has_other_roles(settings_stub, monkeypatch, other_role):
    # A provider that also handles chat or images has to pass the chat test, otherwise that role could
    # be broken while the test still reported success.
    transcriptions = _patch_transcription(monkeypatch)
    _patch_ping(monkeypatch, text_response=None)

    provider = _make_test_provider()
    repos = _make_mock_repos()
    settings = repos.group_ai_provider_settings.get_one.return_value
    settings.audio_provider_id = provider.id
    setattr(settings, other_role, provider.id)

    result = await OpenAIService(repos).test_connection(provider)

    assert result.success is False
    assert transcriptions.calls == []


@pytest.mark.asyncio
async def test_connection_skips_transcription_for_non_audio_provider(settings_stub, monkeypatch):
    transcriptions = _patch_transcription(monkeypatch)
    _patch_ping(monkeypatch, image_response="Tomato & Egg Stir-Fry")

    result = await OpenAIService(_make_mock_repos()).test_connection(_make_test_provider())

    assert result.success is True
    assert transcriptions.calls == []
