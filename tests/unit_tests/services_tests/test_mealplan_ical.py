from mealie.services.household_services.mealplan_ical_service import _escape_text, _fold


def test_escape_text():
    assert _escape_text("a\\b;c,d\r\ne\nf") == "a\\\\b\\;c\\,d\\ne\\nf"


def test_fold_short_line_unchanged():
    assert _fold("SUMMARY:Dinner") == "SUMMARY:Dinner"


def test_fold_long_line():
    line = "DESCRIPTION:" + "x" * 200
    folded = _fold(line)

    parts = folded.split("\r\n")
    assert len(parts) > 1
    assert all(len(part.encode()) <= 75 for part in parts)
    assert all(part.startswith(" ") for part in parts[1:])
    assert folded.replace("\r\n ", "") == line


def test_fold_does_not_split_multibyte_characters():
    line = "SUMMARY:" + "🍝ä" * 40
    folded = _fold(line)

    parts = folded.split("\r\n")
    assert all(len(part.encode()) <= 75 for part in parts)
    assert folded.replace("\r\n ", "") == line
