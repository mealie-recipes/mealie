import re
from fractions import Fraction

compiled_match = re.compile(r"(.){1,6}\s\((.[^\(\)])+\)\s")
compiled_search = re.compile(r"\((.[^\(])+\)")


def move_parens_to_end(ing_str) -> str:
    """
    Moves all parentheses in the string to the end of the string using Regex.
    If no parentheses are found, the string is returned unchanged.
    """
    if re.match(compiled_match, ing_str):
        if match := re.search(compiled_search, ing_str):
            start = match.start()
            end = match.end()
            ing_str = ing_str[:start] + ing_str[end:] + " " + ing_str[start:end]

    return ing_str


def check_char(char, *eql) -> bool:
    """Helper method to check if a characters matches any of the additional provided arguments"""
    return any(char == eql_char for eql_char in eql)


def convert_vulgar_fractions_to_regular_fractions(text: str) -> str:
    vulgar_fractions = {
        "¼": "1/4",
        "½": "1/2",
        "¾": "3/4",
        "⅐": "1/7",
        "⅑": "1/9",
        "⅒": "1/10",
        "⅓": "1/3",
        "⅔": "2/3",
        "⅕": "1/5",
        "⅖": "2/5",
        "⅗": "3/5",
        "⅘": "4/5",
        "⅙": "1/6",
        "⅚": "5/6",
        "⅛": "1/8",
        "⅜": "3/8",
        "⅝": "5/8",
        "⅞": "7/8",
    }

    for vulgar_fraction, regular_fraction in vulgar_fractions.items():
        # if we don't add a space in front of the fraction, mixed fractions will be broken
        # e.g. "1½" -> "11/2"
        text = text.replace(vulgar_fraction, f" {regular_fraction}").strip()

    return text


def extract_quantity_from_string(source_str: str) -> tuple[float, str]:
    """
    Extracts a quantity from a string. The quantity can be a fraction, decimal, or integer.

    Returns the quantity and the remaining string. If no quantity is found, returns the quantity as 0.
    """

    source_str = source_str.strip()
    if not source_str:
        return 0, ""

    source_str = convert_vulgar_fractions_to_regular_fractions(source_str)

    mixed_fraction_pattern = re.compile(r"(\d+)\s+(\d+)/(\d+)")
    fraction_pattern = re.compile(r"(\d+)/(\d+)")
    number_pattern = re.compile(r"\d+(\.\d+)?")

    try:
        # Check for a mixed fraction (e.g. "1 1/2")
        match = mixed_fraction_pattern.search(source_str)
        if match:
            whole_number = int(match.group(1))
            numerator = int(match.group(2))
            denominator = int(match.group(3))
            quantity = whole_number + float(Fraction(numerator, denominator))
            remaining_str = source_str[: match.start()] + source_str[match.end() :]

            remaining_str = remaining_str.strip()
            return quantity, remaining_str

        # Check for a fraction (e.g. "1/2")
        match = fraction_pattern.search(source_str)
        if match:
            numerator = int(match.group(1))
            denominator = int(match.group(2))
            quantity = float(Fraction(numerator, denominator))
            remaining_str = source_str[: match.start()] + source_str[match.end() :]

            remaining_str = remaining_str.strip()
            return quantity, remaining_str

        # Check for a number (integer or float)
        match = number_pattern.search(source_str)
        if match:
            quantity = float(match.group())
            remaining_str = source_str[: match.start()] + source_str[match.end() :]

            remaining_str = remaining_str.strip()
            return quantity, remaining_str

    except ZeroDivisionError:
        pass

    # If no match, return 0 and the original string
    return 0, source_str
