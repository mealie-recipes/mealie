from pathlib import Path

from mealie.services.ocr.pytesseract import OcrService

ocr_service = OcrService()


def test_image_to_string():
    with open(Path("tests/data/images/test-ocr.png"), "rb") as image:
        result = ocr_service.image_to_string(image)
        with open(Path("tests/data/text/test-ocr.txt"), "r", encoding="utf-8") as expected_result:
            assert result == expected_result.read()


def test_image_to_tsv():
    with open(Path("tests/data/images/test-ocr.png"), "rb") as image:
        result = ocr_service.image_to_tsv(image.read())
        with open(Path("tests/data/text/test-ocr.tsv"), "r", encoding="utf-8") as expected_result:
            assert result == expected_result.read()
