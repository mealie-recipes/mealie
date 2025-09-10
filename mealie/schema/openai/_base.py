import re
from typing import Self

from pydantic import BaseModel

from mealie.core.root_logger import get_logger

RE_NULLS = re.compile(r"[\x00\u0000]|\\u0000")

logger = get_logger()


class OpenAIBase(BaseModel):
    """
    This class defines the JSON schema sent to OpenAI. Its schema is
    injected directly into the OpenAI prompt.
    """

    __doc__ = ""  # we don't want to include the docstring in the JSON schema

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
