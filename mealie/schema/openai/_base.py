from pydantic import BaseModel

from mealie.core.root_logger import get_logger

logger = get_logger()


class OpenAIBase(BaseModel):
    """
    This class defines the JSON schema sent to OpenAI. Its schema is
    injected directly into the OpenAI prompt.
    """

    __doc__ = ""  # we don't want to include the docstring in the JSON schema

    @classmethod
    def parse_openai_response(cls, response: str | None):
        """
        This method should be implemented in the child class. It should
        parse the JSON response from OpenAI and return a dictionary.
        """

        try:
            return cls.model_validate_json(response or "")
        except Exception:
            logger.debug(f"Failed to parse OpenAI response as {cls}. Response: {response}")
            raise
