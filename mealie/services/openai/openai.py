import base64
import inspect
import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from textwrap import dedent
from typing import TypeVar

import openai
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel, field_validator

from mealie.core import exceptions, root_logger
from mealie.core.config import get_app_settings
from mealie.pkgs import img
from mealie.schema.openai._base import OpenAIBase
from mealie.schema.openai.general import OpenAIText

from .._base_service import BaseService

T = TypeVar("T", bound=OpenAIBase)
logger = root_logger.get_logger(__name__)


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
        image = img.PillowMinifier.to_jpg(
            self.path, dest=self.path.parent.joinpath(f"{self.filename}-min-original.jpg")
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

    def __init__(self) -> None:
        settings = get_app_settings()
        if not settings.OPENAI_ENABLED:
            raise ValueError("OpenAI is not enabled")

        self.model = settings.OPENAI_MODEL
        self.audio_model = settings.OPENAI_AUDIO_MODEL
        self.workers = settings.OPENAI_WORKERS
        self.send_db_data = settings.OPENAI_SEND_DATABASE_DATA
        self.custom_prompt_dir = settings.OPENAI_CUSTOM_PROMPT_DIR

        self.get_client = lambda: AsyncOpenAI(
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.OPENAI_REQUEST_TIMEOUT,
            default_headers=settings.OPENAI_CUSTOM_HEADERS,
            default_query=settings.OPENAI_CUSTOM_PARAMS,
        )

        super().__init__()

    def _get_prompt_file_candidates(self, name: str) -> list[Path]:
        """
        Returns a list of prompt file path candidates.
        First optional entry is the users custom prompt file, if configured and existing,
        second one (or only one) is the systems default prompt file
        """
        tree = name.split(".")
        relative_path = Path(*tree[:-1], tree[-1] + ".txt")
        default_prompt_file = Path(self.PROMPTS_DIR, relative_path)

        try:
            # Only include custom files if the custom_dir is configured, is a directory, and the prompt file exists
            custom_dir = Path(self.custom_prompt_dir) if self.custom_prompt_dir else None
            if custom_dir and not custom_dir.is_dir():
                custom_dir = None
        except Exception:
            custom_dir = None

        if custom_dir:
            custom_prompt_file = Path(custom_dir, relative_path)
            if custom_prompt_file.exists():
                logger.debug(f"Found valid custom prompt file: {custom_prompt_file}")
                return [custom_prompt_file, default_prompt_file]
            else:
                logger.debug(f"Custom prompt file doesn't exist: {custom_prompt_file}")
        else:
            logger.debug(f"Custom prompt dir doesn't exist: {custom_dir}")

        # Otherwise, only return the default internal prompt file
        return [default_prompt_file]

    def _load_prompt_from_file(self, name: str) -> str:
        """Attempts to load custom prompt, otherwise falling back to the default"""
        prompt_file_candidates = self._get_prompt_file_candidates(name)
        content = None
        last_error = None
        for prompt_file in prompt_file_candidates:
            try:
                logger.debug(f"Trying to load prompt file: {prompt_file}")
                with open(prompt_file) as f:
                    content = f.read()
                    if content:
                        logger.debug(f"Successfully read prompt from {prompt_file}")
                        break
            except OSError as e:
                last_error = e

        if not content:
            if last_error:
                raise OSError(f"Unable to load prompt {name}") from last_error
            else:
                # This handles the case where the list was empty (no existing candidates found)
                attempted_paths = ", ".join(map(str, prompt_file_candidates))
                raise OSError(f"Unable to load prompt '{name}'. No valid content found in files: {attempted_paths}")

        return content

    def get_prompt(self, name: str, data_injections: list[OpenAIDataInjection] | None = None) -> str:
        """
        Load stored prompt and inject data into it.

        Access prompts with dot notation.
        For example, to access `prompts/recipes/parse-recipe-ingredients.txt`, use
        `recipes.parse-recipe-ingredients`
        """

        if not name:
            raise ValueError("Prompt name cannot be empty")

        content = self._load_prompt_from_file(name)

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

    async def _get_raw_response(self, prompt: str, content: list[dict], response_schema: type[T]) -> ChatCompletion:
        client = self.get_client()
        return await client.chat.completions.parse(
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
            model=self.model,
            response_format=response_schema,
        )

    async def get_response(
        self,
        prompt: str,
        message: str,
        *,
        response_schema: type[T],
        attachments: list[OpenAIAttachment] | None = None,
    ) -> T | None:
        """Send data to OpenAI and return the response message content"""

        try:
            user_messages = [{"type": "text", "text": message}]
            for attachment in attachments or []:
                user_messages.append(attachment.build_message())

            response = await self._get_raw_response(prompt, user_messages, response_schema)
            if not response.choices:
                return None

            response_text = response.choices[0].message.content
            return response_schema.parse_openai_response(response_text)
        except openai.RateLimitError as e:
            raise exceptions.RateLimitError(str(e)) from e
        except Exception as e:
            raise Exception(f"OpenAI Request Failed. {e.__class__.__name__}: {e}") from e

    async def transcribe_audio(self, audio_file_path: Path) -> str | None:
        client = self.get_client()

        # Create a transcription from the audio
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model=self.audio_model,
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
            self.get_prompt("general.transcribe-audio"),
            "Attached is the audio data.",
            response_schema=OpenAIText,
            attachments=[audio_attachment],
        )

        return response.text if response else None
