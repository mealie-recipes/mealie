import re
from typing import Any, Self

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
    def _resolve_refs(cls, obj: Any, defs: dict) -> Any:
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref_name = obj["$ref"].split("/")[-1]
                return cls._resolve_refs(defs[ref_name], defs)
            return {k: cls._resolve_refs(v, defs) for k, v in obj.items()}
        if isinstance(obj, list):
            return [cls._resolve_refs(item, defs) for item in obj]
        return obj

    @classmethod
    def model_json_schema(cls, **kwargs: Any) -> dict[str, Any]:
        schema = super().model_json_schema(**kwargs)
        defs = schema.pop("$defs", {})
        if defs:
            schema = cls._resolve_refs(schema, defs)
        return schema

    @classmethod
    def _preprocess_response(cls, response: str | None) -> str:
        if not response:
            return ""

        response = re.sub(RE_NULLS, "", response)
        return response

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
