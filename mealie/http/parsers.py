import json
from typing import Any

from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser
from rest_framework.parsers import JSONParser as DRFJSONParser
from rest_framework.parsers import MultiPartParser as DRFMultiPartParser

from mealie.http.api import HTTPException, RequestValidationError


class JSONParser(DRFJSONParser):
    def parse(self, stream: Any, media_type: Any = None, parser_context: Any = None) -> Any:
        try:
            return json.load(stream)
        except json.JSONDecodeError as exc:
            raise RequestValidationError(
                [
                    {
                        "type": "json_invalid",
                        "loc": ("body", exc.pos),
                        "msg": "JSON decode error",
                        "input": {},
                        "ctx": {"error": exc.msg},
                    }
                ]
            ) from exc
        except UnicodeDecodeError as exc:
            raise HTTPException(400, "There was an error parsing the body") from exc


class MultiPartParser(DRFMultiPartParser):
    def parse(self, stream: Any, media_type: Any = None, parser_context: Any = None) -> Any:
        try:
            parsed = super().parse(stream, media_type, parser_context)
        except ParseError as exc:
            if "Invalid boundary in multipart: None" in str(exc):
                raise HTTPException(400, "Missing boundary in multipart.") from exc
            raise
        message = None
        if sum(len(values) for _, values in parsed.files.lists()) > 1000:
            message = "Too many files. Maximum number of files is 1000."
        elif sum(len(values) for _, values in parsed.data.lists()) > 1000:
            message = "Too many fields. Maximum number of fields is 1000."
        elif any(len(value.encode("utf-8")) > 1024 * 1024 for _, values in parsed.data.lists() for value in values):
            message = "Part exceeded maximum size of 1024KB."
        if message:
            for _, files in parsed.files.lists():
                for file in files:
                    file.close()
            raise HTTPException(400, message)
        return parsed


class RawParser(BaseParser):
    media_type = "*/*"

    def parse(self, stream: Any, media_type: Any = None, parser_context: Any = None) -> bytes:
        return stream.read()
