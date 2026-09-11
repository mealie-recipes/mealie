import re
from typing import Self, get_origin

from pydantic import BaseModel

from mealie.core.root_logger import get_logger

RE_NULLS = re.compile(r"[\x00\u0000]|\\u0000")

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
    def _strip_outer_code_fence(cls, response: str) -> str:
        """Remove a single outer markdown code fence, if present.

        Only strips an opening fence at the very start and a closing fence at
        the very end of the response (e.g. ```json\\n{...}\\n```). Backticks
        inside JSON string values are left untouched.
        """
        stripped = response.strip()
        opening = re.match(r"```(?:json)?", stripped, re.IGNORECASE)
        if opening:
            stripped = stripped[opening.end() :].lstrip()
        if stripped.endswith("```"):
            stripped = stripped[: -len("```")].rstrip()
        return stripped

    @classmethod
    def _preprocess_response(cls, response: str | None) -> str:
        if not response:
            return ""

        response = re.sub(RE_NULLS, "", response)

        # Local OpenAI-compatible servers (e.g. Ollama) often wrap JSON in an
        # outer markdown code fence. Strip only the outer fence so markdown
        # inside string values (bold, inline code) is preserved.
        response = cls._strip_outer_code_fence(response)
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
