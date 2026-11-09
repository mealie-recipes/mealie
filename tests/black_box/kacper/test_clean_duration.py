"""Black-box unit tests for clean_duration (KacperM). Test cases are documented in kacperM.md."""

from datetime import timedelta

import pytest

from mealie.services.scraper.cleaner import clean_duration


@pytest.mark.parametrize(
    ("time_entry", "expected"),
    [
        pytest.param("PT1H30M", 5400, id="KM-11"),
        pytest.param(30, 1800, id="KM-12"),
        pytest.param("30", 1800, id="KM-13"),
        pytest.param(timedelta(hours=1), 3600, id="KM-14"),
        pytest.param({"minValue": "PT1H"}, 3600, id="KM-15"),
        pytest.param(["PT1H", "PT2H"], 3600, id="KM-16"),
        pytest.param(None, None, id="KM-17"),
        pytest.param("", None, id="KM-18"),
        pytest.param([], None, id="KM-19"),
        pytest.param(0, None, id="KM-20"),
        pytest.param(-5, None, id="KM-21"),
        pytest.param("PT0S", None, id="KM-22"),
        pytest.param("about 20 minutes", None, id="KM-23"),
        pytest.param(10**12, None, id="KM-24"),
    ],
)
def test_clean_duration(time_entry, expected):
    assert clean_duration(time_entry) == expected
