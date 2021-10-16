import re

compiled_match = re.compile(r"(.){1,6}\s\((.[^\(\)])+\)\s")
compiled_search = re.compile(r"\((.[^\(])+\)")


def move_parens_to_end(ing_str) -> str:
    """
    Moves all parentheses in the string to the end of the string using Regex.
    If no parentheses are found, the string is returned unchanged.
    """
    if re.match(compiled_match, ing_str):
        match = re.search(compiled_search, ing_str)
        start = match.start()
        end = match.end()
        ing_str = ing_str[:start] + ing_str[end:] + " " + ing_str[start:end]

    return ing_str


def check_char(char, *eql) -> bool:
    """Helper method to check if a charaters matches any of the additional provided arguments"""
    return any(char == eql_char for eql_char in eql)
