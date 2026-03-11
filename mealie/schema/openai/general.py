from pydantic import Field

from ._base import OpenAIBase


class OpenAIText(OpenAIBase):
    text: str = Field(..., description="A simple response message")
