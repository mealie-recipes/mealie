from unittest.mock import MagicMock
from uuid import uuid4

import httpx
import openai
import pytest

import mealie.services.openai.openai as openai_module
from mealie.schema.group.ai_providers import AIProviderOut
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
async def test_ping_builds_debug_prompt_and_delegates_to_get_response(settings_stub, monkeypatch):
    monkeypatch.setattr(OpenAIService, "get_prompt", lambda self, name: f"PROMPT:{name}")

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
        "prompt": "PROMPT:general.debug",
        "message": "hello there",
        "attachments": ["fake-image"],
        "provider": provider,
    }


@pytest.mark.asyncio
async def test_connection_success_recognizes_test_image(settings_stub, monkeypatch):
    # The bundled test image is a screenshot of a "Tomato & Egg Stir-Fry" recipe - a response that
    # actually describes it should satisfy the keyword check.
    _patch_ping(monkeypatch, image_response="This looks like a Tomato & Egg Stir-Fry with eggs and tomato.")

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is True
    assert result.message is None
    assert result.image_test_passed is True


@pytest.mark.asyncio
async def test_connection_success_but_image_reply_does_not_mention_recipe(settings_stub, monkeypatch):
    # Some providers accept an image parameter without erroring but don't actually look at it -
    # the text check alone can't tell the two apart, which is the whole point of this second step.
    _patch_ping(monkeypatch, image_response="I'm not sure what you mean, could you clarify?")

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is True
    assert result.image_test_passed is False
    assert result.image_test_message is None  # a clean miss, not an error - nothing to show


@pytest.mark.asyncio
async def test_connection_success_but_image_request_errors(settings_stub, monkeypatch):
    # e.g. a text-only model that rejects an image_url content part outright
    _patch_ping(monkeypatch, image_error=Exception("model does not support image input"))

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is True
    assert result.image_test_passed is False
    assert result.image_test_message is not None
    assert "model does not support image input" in result.image_test_message


@pytest.mark.asyncio
async def test_connection_text_failure_never_attempts_image_test(settings_stub, monkeypatch):
    calls: list[list | None] = []

    async def _fake_ping(self, provider, message, images=None):
        calls.append(images)
        raise Exception("connection refused")

    monkeypatch.setattr(OpenAIService, "ping", _fake_ping)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is False
    assert result.message is not None
    assert "connection refused" in result.message
    assert result.image_test_passed is None
    assert result.image_test_message is None
    assert calls == [None]  # only the text ping ran


@pytest.mark.asyncio
async def test_connection_empty_response_is_a_failure(settings_stub, monkeypatch):
    _patch_ping(monkeypatch, text_response=None)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is False
    assert result.message == "No response received from the provider."
    assert result.image_test_passed is None


@pytest.mark.asyncio
async def test_connection_failure_truncates_long_error_messages(settings_stub, monkeypatch):
    # A misconfigured base_url can land on something that isn't the intended API at all (a
    # Cloudflare block page, a load balancer default vhost, ...) and return a huge non-JSON body,
    # which the SDK includes verbatim in the exception message. That must not flood the UI.
    huge_html = "<!DOCTYPE html>" + ("<div>error page content</div>\n" * 200)

    async def _fake_ping(self, provider, message, images=None):
        raise Exception(huge_html)

    monkeypatch.setattr(OpenAIService, "ping", _fake_ping)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is False
    assert result.message is not None
    assert len(result.message) <= openai_module._MAX_TEST_ERROR_MESSAGE_LENGTH + 1  # +1 for the "…"
    assert result.message.endswith("…")
    assert "\n" not in result.message


@pytest.mark.asyncio
async def test_connection_extracts_clean_message_from_api_status_error(settings_stub, monkeypatch):
    # get_response() wraps every failure into a plain Exception before it reaches test_connection,
    # so the raw exception text is the SDK's dict repr of the whole response body (ugly, and not
    # what the user actually needs to see) - the real, human-written message is only reachable via
    # __cause__. This proves that extraction actually works against the real SDK error type.
    response = httpx.Response(
        status_code=404,
        request=httpx.Request("POST", "https://example.com/v1/chat/completions"),
        content=b"irrelevant, .body below is what's read",
    )
    sdk_error = openai.NotFoundError(
        message="Error code: 404 - {'error': {'message': 'model not found', ...}}",
        response=response,
        body={"error": {"message": "The model `gpt-4o-mini111` does not exist or you do not have access to it."}},
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
    assert result.message == "HTTP 404: The model `gpt-4o-mini111` does not exist or you do not have access to it."
