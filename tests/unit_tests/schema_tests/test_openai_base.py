import pydantic
import pytest

from mealie.schema.openai._base import OpenAIBase


class _SampleSchema(OpenAIBase):
    answer: str


def test_parse_openai_response_plain_json():
    result = _SampleSchema.parse_openai_response('{"answer": "hi"}')
    assert result.answer == "hi"


def test_parse_openai_response_strips_json_markdown_fence():
    response = '```json\n{"answer": "hi"}\n```'
    result = _SampleSchema.parse_openai_response(response)
    assert result.answer == "hi"


def test_parse_openai_response_strips_bare_markdown_fence():
    response = '```\n{"answer": "hi"}\n```'
    result = _SampleSchema.parse_openai_response(response)
    assert result.answer == "hi"


def test_parse_openai_response_strips_fence_with_surrounding_whitespace():
    response = '  \n```json\n{"answer": "hi"}\n```\n  '
    result = _SampleSchema.parse_openai_response(response)
    assert result.answer == "hi"


def test_parse_openai_response_strips_null_bytes():
    result = _SampleSchema.parse_openai_response('{"answer": "nul\x00l"}')
    assert result.answer == "null"


def test_parse_openai_response_strips_escaped_null_bytes():
    result = _SampleSchema.parse_openai_response('{"answer": "nul\\u0000l"}')
    assert result.answer == "null"


def test_parse_openai_response_raises_on_prose():
    with pytest.raises(pydantic.ValidationError):
        _SampleSchema.parse_openai_response("this is plain prose, not JSON")


def test_parse_openai_response_raises_on_fenced_prose():
    with pytest.raises(pydantic.ValidationError):
        _SampleSchema.parse_openai_response("```json\nthis is plain prose, not JSON\n```")


def test_parse_openai_response_raises_on_empty_response():
    with pytest.raises(pydantic.ValidationError):
        _SampleSchema.parse_openai_response(None)
