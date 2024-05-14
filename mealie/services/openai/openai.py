import inspect
import json
import os
from pathlib import Path
from textwrap import dedent

from openai import NOT_GIVEN, AsyncOpenAI
from openai.resources.chat.completions import ChatCompletion
from pydantic import BaseModel, field_validator

from mealie.core.config import get_app_settings

from .._base_service import BaseService


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


class OpenAIService(BaseService):
    PROMPTS_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "prompts"

    def __init__(self) -> None:
        settings = get_app_settings()
        if not settings.OPENAI_ENABLED:
            raise ValueError("OpenAI is not enabled")

        self.model = settings.OPENAI_MODEL
        self.workers = settings.OPENAI_WORKERS
        self.send_db_data = settings.OPENAI_SEND_DATABASE_DATA

        self.get_client = lambda: AsyncOpenAI(
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY,
        )

        super().__init__()

    @classmethod
    def get_prompt(cls, name: str, data_injections: list[OpenAIDataInjection] | None = None) -> str:
        """
        Load stored prompt and inject data into it.

        Access prompts with dot notation.
        For example, to access `prompts/recipes/parse-recipe-ingredients.txt`, use
        `recipes.parse-recipe-ingredients`
        """

        if not name:
            raise ValueError("Prompt name cannot be empty")

        tree = name.split(".")
        prompt_dir = os.path.join(cls.PROMPTS_DIR, *tree[:-1], tree[-1] + ".txt")
        try:
            with open(prompt_dir) as f:
                content = f.read()
        except OSError as e:
            raise OSError(f"Unable to load prompt {name}") from e

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
        self, prompt: str, message: str, temperature=0.2, force_json_response=True
    ) -> ChatCompletion:
        client = self.get_client()
        return await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            model=self.model,
            temperature=temperature,
            response_format={"type": "json_object"} if force_json_response else NOT_GIVEN,
        )

    async def get_response(self, prompt: str, message: str, temperature=0.2, force_json_response=True) -> str | None:
        """Send data to OpenAI and return the response message content"""
        try:
            response = await self._get_raw_response(prompt, message, temperature, force_json_response)
            if not response.choices:
                return None
            return response.choices[0].message.content
        except Exception:
            self.logger.exception("OpenAI Request Failed")
            return None
