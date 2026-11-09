"""Black-box unit tests for clean_image (KacperM). Test cases are documented in kacperM.md."""

import pytest

from mealie.services.scraper.cleaner import NO_IMAGE, clean_image

URL = "https://example.com/a.jpg"
URL_2 = "https://example.com/b.jpg"


# sprawdzamy poprawne wartości (nie powinien wywalić błędu)
@pytest.mark.parametrize(
    ("image", "default", "expected"),
    [
        pytest.param(URL, NO_IMAGE, [URL], id="KM-25"),
        pytest.param({"url": URL}, NO_IMAGE, [URL], id="KM-26"),
        pytest.param([URL, URL_2], NO_IMAGE, [URL, URL_2], id="KM-27"),
        pytest.param([{"url": URL}, {"url": URL_2}], NO_IMAGE, [URL, URL_2], id="KM-28"),
        pytest.param(None, NO_IMAGE, [NO_IMAGE], id="KM-29"),
        pytest.param("", NO_IMAGE, [NO_IMAGE], id="KM-30"),
        pytest.param([], NO_IMAGE, [NO_IMAGE], id="KM-31"),
        pytest.param({}, NO_IMAGE, [NO_IMAGE], id="KM-32"),
        pytest.param(None, URL_2, [URL_2], id="KM-33"),
    ],
)
def test_clean_image(image, default, expected):
    assert clean_image(image, default) == expected


# sprawdzamy niepoprawne wartości, czy zgłosi TypeError
@pytest.mark.parametrize(
    "image",
    [
        pytest.param(123, id="KM-34"),
        pytest.param({"src": URL}, id="KM-35"),
        pytest.param([1, 2], id="KM-36"),
    ],
)
def test_clean_image_unsupported_type(image):
    try:
        result = clean_image(image)
    except TypeError:
        return
    pytest.fail(f"Nie zgłoszono TypeError, funkcja zwróciła: {result!r}")
