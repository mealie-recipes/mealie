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
