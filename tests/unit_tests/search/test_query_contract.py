import pytest

from mealie.search.query import Clause, correction, normalize, parse


@pytest.mark.parametrize(
    ("source", "clauses"),
    [
        ("pork lettuce wrap", (Clause("pork"), Clause("lettuce wrap"))),
        ('"lettuce cups" pork', (Clause("lettuce cups", "phrase"), Clause("pork"))),
        ('+pork -"chili peppers"', (Clause("pork", "required"), Clause("chili peppers", "excluded"))),
        ("-cilantro", (Clause("cilantro", "excluded"),)),
        ("cook's sesame-lime", (Clause("cook s"), Clause("sesame lime"))),
        ("%pork% _lettuce_", (Clause("pork"), Clause("lettuce"))),
        ("lettuce +wrap", (Clause("lettuce"), Clause("wrap", "required"))),
        ('lettuce "wrap"', (Clause("lettuce"), Clause("wrap", "phrase"))),
        ("lettuce -wrap", (Clause("lettuce"), Clause("wrap", "excluded"))),
        ("cup wrap", (Clause("cup"), Clause("wrap"))),
        ("  ", ()),
    ],
)
def test_clause_contract(source: str, clauses: tuple[Clause, ...]) -> None:
    assert parse(source).clauses == clauses
    assert parse(source, "any").clauses == clauses
    assert parse(source, "any").mode == "any"


@pytest.mark.parametrize("source", ['"unfinished', 'unfinished"', '""', "+", "-", "+ ", '-""', '"pork"lettuce'])
def test_invalid_syntax(source: str) -> None:
    with pytest.raises(ValueError):
        parse(source)


def test_input_limits() -> None:
    assert parse("a" * 512).clauses == (Clause("a" * 512),)
    with pytest.raises(ValueError, match="512"):
        parse("a" * 513)
    assert len(parse(" ".join(["pork"] * 32)).clauses) == 32
    with pytest.raises(ValueError, match="32"):
        parse(" ".join(["pork"] * 33))


@pytest.mark.parametrize("kind", ["required", "excluded", "phrase"])
def test_literals_do_not_expand(kind: str) -> None:
    clause = next(
        item for item in parse('+"lettuce wraps" -"lettuce wraps" "lettuce wraps"').clauses if item.kind == kind
    )
    assert clause.alternatives == ("lettuce wraps",)


@pytest.mark.parametrize(
    ("source", "prefix"),
    [
        ("pork", True),
        ("lettuce wrap", False),
        ("pork lettuce", False),
        ("+pork", False),
        ('"pork"', False),
        ("-pork", False),
    ],
)
def test_prefix_only_for_one_ordinary_word(source: str, prefix: bool) -> None:
    assert parse(source).prefix is prefix


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Crème brûlée", "creme brulee"),
        ("Straße Æsir Œuf Ø Ł Đ Þ", "strasse aesir oeuf o l d th"),
        ("北 京 猪肉", "北 京 猪肉"),
        ("Курица Σαλάτα", "курица σαλατα"),
        ("pork\tlettuce\nwrap", "pork lettuce wrap"),
        ("%_\"'()*:!-+", ""),
    ],
)
def test_normalization_contract(source: str, expected: str) -> None:
    assert normalize(source) == expected
    assert normalize(expected) == expected


def test_typo_correction_rejects_short_ambiguous_and_distant_terms() -> None:
    assert correction("pork", {"porky"}) is None
    assert correction("carrot", {"carrots"}) == "carrots"
    assert correction("carrot", {"carrots", "parrot"}) is None
    assert correction("lettuse", {"lettuce"}) == "lettuce"
    assert correction("lettuse", {"chicken"}) is None
    assert correction("lettuse", set()) is None


def test_equivalents_have_bounded_alternatives() -> None:
    for source in ("lettuce wraps", "lettuce wrap", "lettuce cup", "lettuce cups", "carrots", "berry"):
        alternatives = parse(source).clauses[0].alternatives
        assert source in alternatives
        assert len(alternatives) <= 4


@pytest.mark.parametrize(
    ("singular", "plural"),
    [
        ("tomato", "tomatoes"),
        ("potato", "potatoes"),
        ("cookie", "cookies"),
        ("chili", "chilies"),
        ("berry", "berries"),
        ("taco", "tacos"),
        ("pea", "peas"),
        ("egg", "eggs"),
        ("dish", "dishes"),
    ],
)
def test_common_plural_contract(singular: str, plural: str) -> None:
    assert plural in Clause(singular).alternatives
    assert singular in Clause(plural).alternatives
    for word in (singular, plural):
        assert len(Clause(word).alternatives) <= 4
        assert Clause(word, "required").alternatives == (word,)
        assert Clause(word, "excluded").alternatives == (word,)
