import pytesseract
from PIL import Image

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
