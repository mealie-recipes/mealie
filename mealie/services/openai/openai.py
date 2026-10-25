from __future__ import annotations

import base64
import hashlib
import inspect
import io
import json
import os
import shutil
import wave
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from openai import AsyncOpenAI

from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator

from mealie.core import exceptions
from mealie.pkgs import img
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.ai_providers import (
    AIPromptMode,
    AIPromptOut,
    AIPromptOverrideCreate,
    AIPromptOverrideOut,
    AIPromptOverrideUpdate,
    AIPromptsOut,
    AIProviderOut,
    AIProviderTestResult,
)
from mealie.schema.openai._base import OpenAIBase
from mealie.schema.openai.general import OpenAIText

from .._base_service import BaseService

T = TypeVar("T", bound=OpenAIBase)

GLOBAL_PROMPT_NAME = "global"
"""Reserved override name for instructions appended to every user prompt"""

SYSTEM_PROMPT_CATEGORY = "system"
"""
Prompts in this category faithfully transcribe the user's source rather than produce a recipe,
so group-wide instructions (e.g. "use metric units") aren't applied to them
"""


class OpenAINotEnabledException(Exception):
    def __init__(self, message: str = "OpenAI not enabled"):
        self.message = message
        super().__init__(self.message)


class OpenAIDataInjection(BaseModel):
    description: str
    value: str

    @field_validator("value", mode="before")
    def parse_value(cls, value):
        if not value:
            raise ValueError("Value cannot be empty")
        if isinstance(value, str):
            return value

        # convert Pydantic models to JSON
        if isinstance(value, BaseModel):
            return value.model_dump_json()

        # convert Pydantic types to their JSON schema definition
        if inspect.isclass(value) and issubclass(value, BaseModel):
            value = value.model_json_schema()

        # attempt to convert object to JSON
        try:
            return json.dumps(value, separators=(",", ":"))
        except TypeError:
            return value


class OpenAIAttachment(BaseModel, ABC):
    @abstractmethod
    def build_message(self) -> dict: ...


class OpenAIImageBase(OpenAIAttachment):
    @abstractmethod
    def get_image_url(self) -> str: ...

    def build_message(self) -> dict:
        return {
            "type": "image_url",
            "image_url": {"url": self.get_image_url()},
        }


class OpenAIImageExternal(OpenAIImageBase):
    url: str

    def get_image_url(self) -> str:
        return self.url


class OpenAILocalImage(OpenAIImageBase):
    filename: str
    path: Path

    def get_image_url(self) -> str:
        # Downscale and re-encode at a moderate quality before base64-encoding for the
        # provider. The previous default (quality=100, no resize) inflated typical phone
        # photos well past their original size, exceeding stricter providers' image-size
        # limits (e.g. Anthropic's OpenAI-compatible endpoint rejects images >10MB
        # base64-encoded). Vision models downscale internally, so this loses no accuracy.
        image = img.PillowMinifier.to_jpg(
            self.path,
            dest=self.path.parent.joinpath(f"{self.filename}-min-original.jpg"),
            quality=80,
            max_dimension=2048,
        )
        with open(image, "rb") as f:
            b64content = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64content}"


class OpenAILocalAudio(OpenAIAttachment):
    data: str
    format: str

    def build_message(self) -> dict:
        return {
            "type": "input_audio",
            "input_audio": {"data": self.data, "format": self.format},
        }


class OpenAIService(BaseService):
    PROMPTS_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "prompts"
    TESTING_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "testing"

    def __init__(self, repos: AllRepositories) -> None:
        self.repos = repos
        self.provider_settings = repos.group_ai_provider_settings.get_one(repos.group_id)

        # Load providers
        self.default_provider = (
            self.repos.group_ai_providers.get_one(self.provider_settings.default_provider_id)
            if self.provider_settings and self.provider_settings.default_provider_id
            else None
        )
        self.audio_provider = (
            self.repos.group_ai_providers.get_one(self.provider_settings.audio_provider_id)
            if self.provider_settings and self.provider_settings.audio_provider_id
            else None
        )
        self.image_provider = (
            self.repos.group_ai_providers.get_one(self.provider_settings.image_provider_id)
            if self.provider_settings and self.provider_settings.image_provider_id
            else None
        )

        super().__init__()

    def get_client(self, provider: AIProviderOut) -> AsyncOpenAI:
        from openai import AsyncOpenAI

        return AsyncOpenAI(
            base_url=provider.base_url or None,
            api_key=provider.api_key,
            timeout=provider.timeout,
            default_headers=provider.request_headers or None,
            default_query=provider.request_params or None,
        )

    async def ping(
        self, provider: AIProviderOut, message: str, images: list[OpenAILocalImage] | None = None
    ) -> OpenAIText | None:
        """Send a one-off chat message to a provider. Shared by the admin debug endpoint and test_connection."""
        prompt = (self.TESTING_DIR / "debug.txt").read_text()
        return await self.get_response(
            prompt, message, response_schema=OpenAIText, attachments=images, provider=provider
        )

    async def test_connection(self, provider: AIProviderOut) -> AIProviderTestResult:
        """
        Confirm a provider's base_url/api_key/model actually work by sending a real chat message,
        rather than just listing models - a provider can pass a /models check and still fail to
        complete a request (see discussion #8051).

        If that succeeds, additionally report whether the provider can read an image, so someone
        setting one up learns at config time that it can't be used as the image provider, rather
        than when a recipe-from-image import fails later. That's reported as capability info, not
        as a failure: a text-only provider is a perfectly valid setup.

        A provider that's only used as the group's audio provider is tested the way an import uses
        it: transcription first, then the chat message. A transcription-only model (e.g.
        gpt-4o-mini-transcribe) can't answer a chat message, so testing it with chat alone would
        always report a failure for a provider that works fine.
        """
        if self._is_audio_only(provider) and await self._check_transcription(provider):
            return AIProviderTestResult(success=True)

        try:
            response = await self.ping(provider, "Hello, checking to see if I can reach you.")
        except Exception as e:
            # Report the error type/status only, never the provider's response body: this route is
            # open to group managers, who could otherwise point base_url at an internal host and
            # read its error pages back through the test result. The full error is logged instead,
            # where it's only visible to whoever runs the server.
            self.logger.exception("AI provider connection test failed")
            cause = e.__cause__ or e
            status = getattr(cause, "status_code", None)
            name = type(cause).__name__
            return AIProviderTestResult(success=False, message=f"{name} (HTTP {status})" if status else name)

        if not response:
            return AIProviderTestResult(success=False, message="No response received from the provider.")

        return AIProviderTestResult(success=True, supports_images=await self._check_image_support(provider))

    async def _check_image_support(self, provider: AIProviderOut) -> bool:
        """
        Best-effort check of whether this provider can actually read an image, by sending it a
        bundled screenshot of a short recipe (see `testing/`) and looking for that recipe in the
        reply. Advisory only - a provider that can't do this is still perfectly usable for
        everything except the image provider role.
        """
        from mealie.core.dependencies.dependencies import get_temporary_path

        try:
            with get_temporary_path() as temp_path:
                image_path = temp_path / "recipe-image.jpg"
                shutil.copyfile(self.TESTING_DIR / "recipe-image.jpg", image_path)

                response = await self.ping(
                    provider,
                    "Read the attached image and reply in English with the recipe title exactly as written in it.",
                    images=[OpenAILocalImage(filename=image_path.name, path=image_path)],
                )
        except Exception:
            return False

        if not response:
            return False

        keywords = json.loads((self.TESTING_DIR / "recipe.json").read_text())["test_keywords"]
        return any(keyword.lower() in response.text.lower() for keyword in keywords)

    def _is_audio_only(self, provider: AIProviderOut) -> bool:
        """
        Whether this saved provider is the group's audio provider and has no other role. An unsaved
        provider being tested gets a fresh id, so it never matches.
        """
        settings = self.provider_settings
        if not settings or provider.id != settings.audio_provider_id:
            return False
        return provider.id not in (settings.default_provider_id, settings.image_provider_id)

    async def _check_transcription(self, provider: AIProviderOut) -> bool:
        """
        Best-effort check that a provider can transcribe audio, by sending it a second of silence.
        Only whether the request succeeds matters, not what text comes back.
        """
        try:
            await self.get_client(provider).audio.transcriptions.create(
                model=provider.model,
                file=("connection-test.wav", self._silent_wav(), "audio/wav"),
            )
        except Exception:
            self.logger.debug("AI provider transcription test failed", exc_info=True)
            return False
        return True

    @staticmethod
    def _silent_wav(seconds: float = 1.0, sample_rate: int = 16000) -> bytes:
        """A short mono 16-bit WAV of silence, built in memory so no test asset has to be bundled."""
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(b"\x00\x00" * int(sample_rate * seconds))
        return buffer.getvalue()

    def _get_provider(self, attachments: list[OpenAIAttachment] | None = None) -> AIProviderOut:
        """Select the appropriate provider based on attachment types, falling back to the default."""
        has_image = any(isinstance(a, OpenAIImageBase) for a in (attachments or []))
        has_audio = any(isinstance(a, OpenAILocalAudio) for a in (attachments or []))

        if has_image and has_audio:
            raise ValueError("Cannot process both images and audio in one request")

        if has_image:
            if not self.image_provider:
                raise OpenAINotEnabledException("No image provider set")
            return self.image_provider

        if has_audio:
            if not self.audio_provider:
                raise OpenAINotEnabledException("No audio provider set")
            return self.audio_provider

        else:
            if not self.default_provider:
                raise OpenAINotEnabledException("No default provider set")
            return self.default_provider

    @classmethod
    def _get_default_prompt_file(cls, name: str) -> Path:
        tree = name.split(".")
        default_prompt_file = (cls.PROMPTS_DIR / Path(*tree[:-1], tree[-1] + ".txt")).resolve()
        if not default_prompt_file.is_relative_to(cls.PROMPTS_DIR.resolve()):
            raise ValueError(f"Invalid prompt name '{name}': resolves outside prompts directory")

        return default_prompt_file

    @staticmethod
    def is_system_prompt(name: str) -> bool:
        return name.split(".")[0] == SYSTEM_PROMPT_CATEGORY

    @classmethod
    def get_prompt_names(cls) -> list[str]:
        """Every built-in prompt, user prompts first"""
        names = [
            ".".join(path.relative_to(cls.PROMPTS_DIR).with_suffix("").parts) for path in cls.PROMPTS_DIR.rglob("*.txt")
        ]
        return sorted(names, key=lambda name: (cls.is_system_prompt(name), name))

    @classmethod
    def get_default_prompt(cls, name: str) -> str:
        """The built-in prompt, ignoring any customizations"""
        try:
            content = cls._get_default_prompt_file(name).read_text()
        except OSError as e:
            raise OSError(f"Unable to load prompt '{name}'") from e

        if not content:
            raise OSError(f"Unable to load prompt '{name}': the prompt file is empty")

        return content

    @staticmethod
    def _hash_prompt(content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()

    def get_prompts(self) -> AIPromptsOut:
        """The group's customizations of every prompt, alongside the built-in prompts"""
        global_override = self._prompt_overrides.get(GLOBAL_PROMPT_NAME)

        prompts: list[AIPromptOut] = []
        for name in self.get_prompt_names():
            default_content = self.get_default_prompt(name)
            prompt = AIPromptOut(name=name, is_system=self.is_system_prompt(name), default_content=default_content)

            if override := self._prompt_overrides.get(name):
                prompt.mode = override.mode
                prompt.content = override.content
                prompt.default_changed = bool(
                    override.mode == AIPromptMode.override
                    and override.base_prompt_hash
                    and override.base_prompt_hash != self._hash_prompt(default_content)
                )

            prompts.append(prompt)

        return AIPromptsOut(
            global_instructions=global_override.content if global_override else None,
            prompts=prompts,
        )

    def _validate_prompt_name(self, name: str) -> None:
        if name != GLOBAL_PROMPT_NAME and name not in self.get_prompt_names():
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Unknown prompt '{name}'")

    def save_prompt_override(self, name: str, data: AIPromptOverrideUpdate) -> AIPromptsOut:
        """Create or replace the group's customization of a prompt, or of the group-wide instructions"""
        self._validate_prompt_name(name)
        if name == GLOBAL_PROMPT_NAME and data.mode != AIPromptMode.append:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Group-wide instructions can only be appended")

        base_prompt_hash = None if name == GLOBAL_PROMPT_NAME else self._hash_prompt(self.get_default_prompt(name))
        override = AIPromptOverrideCreate(
            name=name, mode=data.mode, content=data.content, base_prompt_hash=base_prompt_hash
        )

        if existing := self._prompt_overrides.get(name):
            self.repos.group_ai_prompt_overrides.update(existing.id, override)
        else:
            self.repos.group_ai_prompt_overrides.create(override)

        self.__dict__.pop("_prompt_overrides", None)
        return self.get_prompts()

    def delete_prompt_override(self, name: str) -> AIPromptsOut:
        """Reset a prompt, or the group-wide instructions, to the default"""
        self._validate_prompt_name(name)
        if existing := self._prompt_overrides.get(name):
            self.repos.group_ai_prompt_overrides.delete(existing.id)

        self.__dict__.pop("_prompt_overrides", None)
        return self.get_prompts()

    @cached_property
    def _prompt_overrides(self) -> dict[str, AIPromptOverrideOut]:
        # Admin-scoped repos aren't tied to a group, so they'd return every group's overrides
        if not self.repos.group_id:
            return {}

        return {override.name: override for override in self.repos.group_ai_prompt_overrides.get_all()}

    def _apply_prompt_overrides(self, name: str, content: str) -> str:
        """
        Apply the group's customizations to a prompt: an override replaces it, while appended
        instructions (the group-wide ones first, then the prompt's own) are added after it.
        Every prompt can be customized, but system prompts don't get the group-wide instructions.
        """
        extra_instructions: list[str] = []
        if not self.is_system_prompt(name) and (global_override := self._prompt_overrides.get(GLOBAL_PROMPT_NAME)):
            extra_instructions.append(global_override.content)

        if override := self._prompt_overrides.get(name):
            if override.mode == AIPromptMode.override:
                content = override.content
            else:
                extra_instructions.append(override.content)

        if not extra_instructions:
            return content

        return "\n".join(
            [
                content,
                "",
                "###",
                "Additional instructions. These take priority over any instructions above that conflict with them.",
                "---",
                "",
                "\n\n".join(extra_instructions),
            ]
        )

    def get_prompt(self, name: str, data_injections: list[OpenAIDataInjection] | None = None) -> str:
        """
        Load stored prompt and inject data into it.

        Access prompts with dot notation.
        For example, to access `prompts/recipes/parse-recipe-ingredients.txt`, use
        `recipes.parse-recipe-ingredients`
        """

        if not name:
            raise ValueError("Prompt name cannot be empty")

        content = self._apply_prompt_overrides(name, self.get_default_prompt(name))

        if not data_injections:
            return content

        content_parts = [content]
        for data_injection in data_injections:
            content_parts.append(
                dedent(
                    f"""
                    ###
                    {data_injection.description}
                    ---

                    {data_injection.value}
                    """
                )
            )
        return "\n".join(content_parts)

    async def _get_raw_response(
        self, prompt: str, content: list[dict], response_schema: type[T], provider: AIProviderOut
    ) -> T | None:
        import openai
        from openai.types.chat import ChatCompletion

        client = self.get_client(provider)
        # parse() builds the same response_format payload create() would send, but its
        # client-side validation runs as a post_parser that the raw-response path never
        # triggers, so we read the body ourselves and let parse_openai_response() below
        # do the parsing (e.g. of markdown-fenced JSON the SDK would otherwise discard).
        async with client.chat.completions.with_streaming_response.parse(
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": content,
                },
            ],
            model=provider.model,
            response_format=response_schema,
        ) as response:
            data = json.loads(await response.text())

        # Mealie doesn't use service_tier, and some OpenAI-compatible providers send values
        # the SDK model rejects (e.g. Groq's "on_demand"), which would fail the whole response.
        if isinstance(data, dict):
            data.pop("service_tier", None)
        completion = ChatCompletion.model_validate(data)

        for choice in completion.choices:
            if choice.finish_reason == "length":
                raise openai.LengthFinishReasonError(completion=completion)
            if choice.finish_reason == "content_filter":
                raise openai.ContentFilterFinishReasonError()

        if not completion.choices:
            return None

        return response_schema.parse_openai_response(completion.choices[0].message.content)

    async def get_response(
        self,
        prompt: str,
        message: str,
        *,
        response_schema: type[T],
        attachments: list[OpenAIAttachment] | None = None,
        provider: AIProviderOut | None = None,
    ) -> T | None:
        """Send data to OpenAI and return the response message content"""
        import openai

        try:
            provider = provider or self._get_provider(attachments)
            user_messages: list[dict] = [{"type": "text", "text": message}]
            for attachment in attachments or []:
                user_messages.append(attachment.build_message())

            return await self._get_raw_response(prompt, user_messages, response_schema, provider)
        except openai.RateLimitError as e:
            raise exceptions.RateLimitError(str(e)) from e
        except Exception as e:
            raise Exception(f"OpenAI Request Failed. {e.__class__.__name__}: {e}") from e

    async def transcribe_audio(self, audio_file_path: Path) -> str | None:
        import openai

        if not self.audio_provider:
            raise OpenAINotEnabledException("No audio provider set")

        client = self.get_client(self.audio_provider)

        # Create a transcription from the audio
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model=self.audio_provider.model,
                    file=audio_file,
                )
            return transcript.text
        except openai.RateLimitError as e:
            raise exceptions.RateLimitError(str(e)) from e
        except Exception as e:
            self.logger.warning(
                f"Failed to create audio transcription, falling back to chat completion ({e.__class__.__name__}: {e})"
            )

        # Fallback to chat completion
        path_obj = Path(audio_file_path)
        with open(path_obj, "rb") as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode("utf-8")

        file_ext = path_obj.suffix.lstrip(".").lower()
        audio_attachment = OpenAILocalAudio(data=audio_data, format=file_ext)
        response = await self.get_response(
            self.get_prompt("system.transcribe-audio"),
            "Attached is the audio data.",
            response_schema=OpenAIText,
            attachments=[audio_attachment],
        )

        return response.text if response else None
