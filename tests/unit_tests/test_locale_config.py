import pytest

from mealie.lang.locale_config import resolve_food_plural, resolve_plural


@pytest.mark.parametrize(
    "source_singular, source_plural, singular, plural, expected",
    [
        pytest.param("onion", "onions", "cebolla", "cebollas", "cebollas", id="translated-plural-is-kept"),
        pytest.param("onion", "onions", "onion", "onions", "onions", id="untranslated-term-keeps-its-plural"),
        pytest.param("garlic", "", "ajo", "", None, id="no-plural-in-either-locale"),
        pytest.param("garlic", None, "ajo", None, None, id="missing-plural-key"),
        # Crowdin can't store an empty translation, so translators repeat the singular instead
        pytest.param("teaspoon", "teaspoons", "茶匙", "茶匙", None, id="plural-repeating-its-own-singular"),
        # ...or they leave the source plural untouched, which leaves it in the wrong language
        pytest.param("cup", "cups", "컵", "cups", None, id="translated-singular-with-source-plural"),
        pytest.param("pound", "lbs", "libra", "lbs", None, id="translated-abbreviation-with-source-plural"),
        # a term the source doesn't pluralize may still pluralize once translated
        pytest.param("celery", "", "sellerie", "sellerien", "sellerien", id="plural-added-by-the-translation"),
        # a plural that legitimately matches the source is dropped; falling back to the singular
        # is safer than rendering the source language
        pytest.param("eggplant", "eggplants", "aubergine", "eggplants", None, id="plural-matching-source-is-dropped"),
    ],
)
def test_resolve_plural(
    source_singular: str, source_plural: str | None, singular: str, plural: str | None, expected: str | None
) -> None:
    assert (
        resolve_plural(source_singular=source_singular, source_plural=source_plural, singular=singular, plural=plural)
        == expected
    )


@pytest.mark.parametrize(
    "locale, expected",
    [
        pytest.param("de-DE", "zwiebeln", id="always-pluralizes"),
        pytest.param("en-US", "zwiebeln", id="pluralizes-without-unit"),
        pytest.param("ja-JP", None, id="never-pluralizes"),
        pytest.param("zh-TW", None, id="never-pluralizes-traditional-chinese"),
        pytest.param(None, "zwiebeln", id="no-locale-falls-back-to-the-string-rules"),
        pytest.param("xx-XX", "zwiebeln", id="unknown-locale-falls-back-to-the-string-rules"),
    ],
)
def test_resolve_food_plural_honors_locale(locale: str | None, expected: str | None) -> None:
    assert (
        resolve_food_plural(
            source_singular="onion", source_plural="onions", singular="zwiebel", plural="zwiebeln", locale=locale
        )
        == expected
    )


def test_resolve_food_plural_never_locale_drops_untranslated_plurals() -> None:
    """A locale that never pluralizes foods drops the plural even when the term is untranslated."""
    assert (
        resolve_food_plural(
            source_singular="onion", source_plural="onions", singular="onion", plural="onions", locale="ja-JP"
        )
        is None
    )
