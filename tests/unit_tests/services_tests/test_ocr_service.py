from pathlib import Path

import pytest

from mealie.services.ocr.pytesseract import OcrService

ocr_service = OcrService()


@pytest.mark.skip("Tesseract is not reliable between environments")
def test_image_to_string():
    with open(Path("tests/data/images/test-ocr.png"), "rb") as image:
        result = ocr_service.image_to_string(image)
        with open(Path("tests/data/text/test-ocr.txt"), encoding="utf-8") as expected_result:
            assert result == expected_result.read()


@pytest.mark.skip("Tesseract is not reliable between environments")
def test_image_to_tsv():
    with open(Path("tests/data/images/test-ocr.png"), "rb") as image:
        result = ocr_service.image_to_tsv(image.read())
        with open(Path("tests/data/text/test-ocr.tsv"), encoding="utf-8") as expected_result:
            assert result == expected_result.read()


def test_format_tsv_output():
    tsv = " level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext \n1\t1\t0\t0\t0\t0\t0\t0\t640\t480\t-1\t\n5\t1\t1\t1\t1\t1\t36\t92\t60\t24\t87.137558\tThis"
    expected_result = [
        {
            "level": 1,
            "page_num": 1,
            "block_num": 0,
            "par_num": 0,
            "line_num": 0,
            "word_num": 0,
            "left": 0,
            "top": 0,
            "width": 640,
            "height": 480,
            "conf": -1.0,
            "text": "",
        },
        {
            "level": 5,
            "page_num": 1,
            "block_num": 1,
            "par_num": 1,
            "line_num": 1,
            "word_num": 1,
            "left": 36,
            "top": 92,
            "width": 60,
            "height": 24,
            "conf": 87.137558,
            "text": "This",
        },
    ]
    assert ocr_service.format_tsv_output(tsv) == expected_result
