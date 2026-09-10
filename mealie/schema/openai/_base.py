import re
from typing import Self, get_origin

from pydantic import BaseModel

from mealie.core.root_logger import get_logger

RE_NULLS = re.compile(r"[\x00\u0000]|\\u0000")
RE_CODE_FENCES = re.compile(r"```(?:json)?", re.IGNORECASE)

logger = get_logger()


class OpenAIBase(BaseModel):
    """
    Base class for OpenAI structured output schemas. These models are passed
    to OpenAI's response_format parameter with strict schema validation.
    """

    __doc__ = ""  # we don't want to include the docstring in the JSON schema

    @classmethod
    def _extract_outermost_json(cls, response: str) -> str:
        """Extract the outermost JSON object or array if surrounded by other text."""
        obj_start = response.find("{")
        arr_start = response.find("[")

        if obj_start == -1 and arr_start == -1:
            return response

        if arr_start != -1 and (obj_start == -1 or arr_start < obj_start):
            start, end_char = arr_start, "]"
        else:
            start, end_char = obj_start, "}"

        end = response.rfind(end_char)
        if end > start:
            return response[start : end + 1]
        return response

    @classmethod
    def _wrap_bare_json_array(cls, response: str) -> str:
        """Wrap a bare JSON array as `{field_name: arr}` when the schema has a list field."""
        if not response.lstrip().startswith("["):
            return response

        for name, field in cls.model_fields.items():
            if get_origin(field.annotation) is list:
                return f'{{"{name}": {response}}}'
        return response

    @classmethod
    def _preprocess_response(cls, response: str | None) -> str:
        if not response:
            return ""

        response = re.sub(RE_NULLS, "", response)

        # Local OpenAI-compatible servers (e.g. Ollama) often wrap JSON in markdown.
        response = RE_CODE_FENCES.sub("", response)
        response = response.replace("**", "")
        response = response.strip()
        response = cls._extract_outermost_json(response)
        return cls._wrap_bare_json_array(response)

    @classmethod
    def _process_response(cls, response: str) -> Self:
        try:
            return cls.model_validate_json(response)
        except Exception:
            logger.debug(f"Failed to parse OpenAI response as {cls}. Response: {response}")
            raise

    @classmethod
    def parse_openai_response(cls, response: str | None) -> Self:
        """
        Parse the OpenAI response into a class instance.
        """

        response = cls._preprocess_response(response)
        return cls._process_response(response)
