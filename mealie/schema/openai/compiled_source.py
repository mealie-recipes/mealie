from pydantic import Field

from ._base import OpenAIBase


class OpenAICompiledSource(OpenAIBase):
    """
    A faithful transcription of whatever source material the user supplied, produced by
    the first step of the recipe import workflow.

    Every field must be derivable without an AI provider, since sources that already contain
    structured data are compiled mechanically.
    """

    contains_recipe: bool = Field(
        ...,
        description="Whether the source contains a recipe at all. Set to false if there is nothing to transcribe.",
    )

    content: str = Field(
        ...,
        description=(
            "The complete source content, transcribed as markdown. Include everything: the title, yield, "
            "times, every ingredient (with any section headings), every instruction step in order, notes, "
            "tips, storage advice, equipment, nutrition information, and attribution. Transcribe, do not "
            "summarize, and do not translate."
        ),
    )

    language: str | None = Field(
        None,
        description="The language the source content is written in, e.g., 'English' or 'French'.",
    )

    image_url: str | None = Field(
        None,
        description="URL of the recipe's image, but only if one appears in the source. Never guess a URL.",
    )
