from unittest.mock import AsyncMock, MagicMock
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


class _FakeModel:
    def __init__(self, model_id: str):
        self.id = model_id


class _FakeModelsResponse:
    def __init__(self, model_ids: list[str]):
        self.data = [_FakeModel(m) for m in model_ids]


def _make_fake_client(*, list_result: AsyncMock) -> MagicMock:
    """A stand-in for AsyncOpenAI that records the timeout passed to with_options()."""
    fake_client = MagicMock()
    fake_client.models.list = list_result

    def _with_options(**kwargs):
        fake_client.with_options_kwargs = kwargs
        return fake_client

    fake_client.with_options.side_effect = _with_options
    return fake_client


@pytest.mark.asyncio
async def test_connection_success_known_model(settings_stub, monkeypatch):
    # Provider fixture uses model="gpt-test", so include it in the fake model list
    response = _FakeModelsResponse(["gpt-test", "gpt-other"])
    fake_client = _make_fake_client(list_result=AsyncMock(return_value=response))
    monkeypatch.setattr(OpenAIService, "get_client", lambda self, provider: fake_client)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is True
    assert result.model_found is True
    assert result.message is None
    assert result.latency_ms is not None
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_connection_succeeds_but_flags_unknown_model(settings_stub, monkeypatch):
    # Connection works, but "gpt-test" (from the provider fixture) isn't in this list
    response = _FakeModelsResponse(["some-other-model"])
    fake_client = _make_fake_client(list_result=AsyncMock(return_value=response))
    monkeypatch.setattr(OpenAIService, "get_client", lambda self, provider: fake_client)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is True
    assert result.model_found is False
    assert result.message is not None
    assert "gpt-test" in result.message


@pytest.mark.asyncio
async def test_connection_empty_model_list_leaves_model_unconfirmed(settings_stub, monkeypatch):
    # Some OpenAI-compatible providers return an empty /v1/models list - not enough evidence
    # to call the configured model wrong, so this should stay a plain, unflagged success.
    response = _FakeModelsResponse([])
    fake_client = _make_fake_client(list_result=AsyncMock(return_value=response))
    monkeypatch.setattr(OpenAIService, "get_client", lambda self, provider: fake_client)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is True
    assert result.model_found is None
    assert result.message is None


@pytest.mark.asyncio
async def test_connection_failure_returns_structured_result(settings_stub, monkeypatch):
    fake_client = _make_fake_client(list_result=AsyncMock(side_effect=Exception("connection refused")))
    monkeypatch.setattr(OpenAIService, "get_client", lambda self, provider: fake_client)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is False
    assert result.latency_ms is None
    assert result.message is not None
    assert "connection refused" in result.message
    # Failures shouldn't raise — callers rely on a structured result, not an exception


@pytest.mark.asyncio
async def test_connection_failure_truncates_long_error_messages(settings_stub, monkeypatch):
    # A misconfigured base_url can land on something that isn't the intended API at all (a
    # Cloudflare block page, a load balancer default vhost, ...) and return a huge non-JSON body,
    # which the SDK includes verbatim in the exception message. That must not flood the UI.
    huge_html = "<!DOCTYPE html>" + ("<div>error page content</div>\n" * 200)
    fake_client = _make_fake_client(list_result=AsyncMock(side_effect=Exception(huge_html)))
    monkeypatch.setattr(OpenAIService, "get_client", lambda self, provider: fake_client)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is False
    assert result.message is not None
    assert len(result.message) <= openai_module._MAX_TEST_ERROR_MESSAGE_LENGTH + 1  # +1 for the "…"
    assert result.message.endswith("…")
    assert "\n" not in result.message


@pytest.mark.asyncio
async def test_connection_api_status_error_includes_status_code(settings_stub, monkeypatch):
    response = httpx.Response(
        status_code=404,
        request=httpx.Request("GET", "https://example.com/v1/models"),
        content=b"Not Found",
    )
    error = openai.NotFoundError(message="Error code: 404", response=response, body=None)

    fake_client = _make_fake_client(list_result=AsyncMock(side_effect=error))
    monkeypatch.setattr(OpenAIService, "get_client", lambda self, provider: fake_client)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is False
    assert result.message is not None
    assert "404" in result.message


@pytest.mark.asyncio
async def test_connection_authentication_error_does_not_leak_key_fragment(settings_stub, monkeypatch):
    response = httpx.Response(
        status_code=401,
        request=httpx.Request("GET", "https://example.com/v1/models"),
        content=b"Unauthorized",
    )
    error = openai.AuthenticationError(
        message="Incorrect API key provided: sk-proj-***************************LEuz.",
        response=response,
        body=None,
    )

    fake_client = _make_fake_client(list_result=AsyncMock(side_effect=error))
    monkeypatch.setattr(OpenAIService, "get_client", lambda self, provider: fake_client)

    svc = OpenAIService(_make_mock_repos())
    result = await svc.test_connection(_make_test_provider())

    assert result.success is False
    assert result.message is not None
    assert "sk-proj" not in result.message
    assert "LEuz" not in result.message


@pytest.mark.asyncio
async def test_connection_uses_its_own_short_timeout(settings_stub, monkeypatch):
    """
    The connectivity check must not block for the provider's full (much longer) functional
    timeout - it should apply its own short-lived override via with_options().
    """
    fake_client = _make_fake_client(list_result=AsyncMock(return_value=_FakeModelsResponse([])))
    monkeypatch.setattr(OpenAIService, "get_client", lambda self, provider: fake_client)

    svc = OpenAIService(_make_mock_repos())
    provider = _make_test_provider()
    assert provider.timeout == 300  # the provider's functional timeout, should NOT be used below

    await svc.test_connection(provider, timeout_seconds=2.0)

    assert fake_client.with_options_kwargs == {"timeout": 2.0}
