from typing import Any

from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaMode


class OpenAIBase(BaseModel):
    """
    This class defines the JSON schema sent to OpenAI. Its schema is
    injected directly into the OpenAI prompt.
    """

    __doc__ = ""  # we don't want to include the docstring in the JSON schema
