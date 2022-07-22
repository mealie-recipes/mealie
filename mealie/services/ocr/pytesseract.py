from io import BytesIO

import pytesseract
from PIL import Image

from mealie.schema.ocr.ocr import OcrTsvResponse
from mealie.services._base_service import BaseService


class OCR(BaseService):
    """
    Class for ocr engines.
    """

    def image_to_string(image_data):
        """
        Returns a plain text translation of an image
        """
        return pytesseract.image_to_string(Image.open(image_data))

    def image_to_tsv(image_data):
        """
        Returns tsv formatted output
        """

        return pytesseract.image_to_data(Image.open(BytesIO(image_data)))

    def format_tsv_output(tsv: str) -> OcrTsvResponse:
        lines = tsv.split("\n")
        titles = [t.strip() for t in lines[0].split("\t")]
        response = []
        #  len-1 because the last line is empty
        for i in range(1, len(lines) - 1):
            d = {}
            for key, value in zip(titles, lines[i].split("\t")):
                if key == "text":
                    d[key] = value.strip()
                elif key == "conf":
                    d[key] = float(value.strip())
                else:
                    d[key] = int(value.strip())

            response.append(d)

        return response
