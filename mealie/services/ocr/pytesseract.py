from io import BytesIO

import pytesseract
from PIL import Image

from mealie.schema.ocr.ocr import OcrTsvResponse
from mealie.services._base_service import BaseService


class OcrService(BaseService):
    """
    Class for ocr engines.
    """

    def image_to_string(self, image_data):
        """
        Returns a plain text translation of an image
        """
        return pytesseract.image_to_string(Image.open(image_data))

    def image_to_tsv(self, image_data, lang=None):
        """
        Returns the pytesseract default tsv output
        """
        if lang is not None:
            return pytesseract.image_to_data(Image.open(BytesIO(image_data)), lang=lang)

        return pytesseract.image_to_data(Image.open(BytesIO(image_data)))

    def format_tsv_output(self, tsv: str) -> list[OcrTsvResponse]:
        """
        Returns a OcrTsvResponse from a default pytesseract tsv output
        """
        lines = tsv.split("\n")
        titles = [t.strip() for t in lines[0].split("\t")]
        response: list[OcrTsvResponse] = []

        for i in range(1, len(lines)):
            if lines[i] == "":
                continue

            line = OcrTsvResponse()
            for key, value in zip(titles, lines[i].split("\t")):
                if key == "text":
                    setattr(line, key, value.strip())
                elif key == "conf":
                    setattr(line, key, float(value.strip()))
                elif key in OcrTsvResponse.__fields__:
                    setattr(line, key, int(value.strip()))
                else:
                    continue

            if isinstance(line, OcrTsvResponse):
                response.append(line)

        return response
