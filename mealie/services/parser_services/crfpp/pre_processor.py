import re
import unicodedata

replace_abbreviations = {
    "cup": " cup ",
    "g": " gram ",
    "kg": " kilogram ",
    "lb": " pound ",
    "ml": " milliliter ",
    "oz": " ounce ",
    "pint": " pint ",
    "qt": " quart ",
    "tbsp": " tablespoon ",
    "tbs": " tablespoon ",  # Order Matters!, 'tsb' must come after 'tbsp' incase of duplicate matches
    "tsp": " teaspoon ",
}


def replace_common_abbreviations(string: str) -> str:

    for k, v in replace_abbreviations.items():
        regex = rf"(?<=\d)\s?({k}s?)"
        string = re.sub(regex, v, string)

    return string


def remove_periods(string: str) -> str:
    """Removes periods not sournded by digets"""
    return re.sub(r"(?<!\d)\.(?!\d)", "", string)


def replace_fraction_unicode(string: str):
    # TODO: I'm not confident this works well enough for production needs some testing and/or refacorting
    # TODO: Breaks on multiple unicode fractions
    for c in string:
        try:
            name = unicodedata.name(c)
        except ValueError:
            continue
        if name.startswith("VULGAR FRACTION"):
            normalized = unicodedata.normalize("NFKC", c)
            numerator, _, denominator = normalized.partition("⁄")  # _ = slash
            text = f" {numerator}/{denominator}"
            return string.replace(c, text).replace("  ", " ")

    return string


def wrap_or_clause(string: str):
    """
    Attempts to wrap or clauses in ()

    Examples:
    '1 tsp. Diamond Crystal or ½ tsp. Morton kosher salt, plus more' -> '1 teaspoon diamond crystal (or 1/2 teaspoon morton kosher salt), plus more'

    """
    # TODO: Needs more adequite testing to be sure this doens't have side effects.
    split_by_or = string.split(" or ")

    split_by_comma = split_by_or[1].split(",")

    if len(split_by_comma) > 0:
        return f"{split_by_or[0]} (or {split_by_comma[0]}),{''.join(split_by_comma[1:])}".strip().removesuffix(",")

    return string


def pre_process_string(string: str) -> str:
    """
    Series of preprocessing functions to make best use of the CRF++ model. The ideal string looks something like...

    {qty} {unit} {food}, {additional}
    1 tbs. wine, expensive or other white wine, plus more

    """
    string = string.lower()
    string = replace_fraction_unicode(string)
    string = remove_periods(string)
    string = replace_common_abbreviations(string)

    if " or " in string:
        string = wrap_or_clause(string)

    return string
