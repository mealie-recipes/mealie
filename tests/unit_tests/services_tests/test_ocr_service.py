from pathlib import Path

from mealie.services.ocr.pytesseract import OCR


def test_image_to_string():
    result = OCR.image_to_string(open(Path("tests/data/images/test-ocr.png"), "rb"))
    expected_result = open(Path("tests/data/text/test-ocr.txt"))
    assert result == expected_result.read()


def test_image_to_tsv():
    result = OCR.image_to_tsv(open(Path("tests/data/images/test-ocr.png"), "rb").read())
    expected_result = open(Path("tests/data/text/test-ocr.tsv"))
    assert result == expected_result.read()
