import string
import unicodedata
from typing import Tuple

from pydantic import BaseModel

from .._helpers import check_char, move_parens_to_end


class BruteParsedIngredient(BaseModel):
    food: str = ""
    note: str = ""
    amount: float = ""
    unit: str = ""

    class Config:
        anystr_strip_whitespace = True


def parse_fraction(x):
    if len(x) == 1 and "fraction" in unicodedata.decomposition(x):
        frac_split = unicodedata.decomposition(x[-1:]).split()
        return float((frac_split[1]).replace("003", "")) / float((frac_split[3]).replace("003", ""))
    else:
        frac_split = x.split("/")
        if len(frac_split) != 2:
            raise ValueError
        try:
            return int(frac_split[0]) / int(frac_split[1])
        except ZeroDivisionError:
            raise ValueError


def parse_amount(ing_str) -> Tuple[float, str, str]:
    def keep_looping(ing_str, end) -> bool:
        """
        Checks if:
        1. the end of the string is reached
        2. or if the next character is a digit
        3. or if the next character looks like an number (e.g. 1/2, 1.3, 1,500)
        """
        if end >= len(ing_str):
            return False

        if ing_str[end] in string.digits:
            return True

        if check_char(ing_str[end], ".", ",", "/") and end + 1 < len(ing_str) and ing_str[end + 1] in string.digits:
            return True

    amount = 0
    unit = ""
    note = ""

    did_check_frac = False
    end = 0

    while keep_looping(ing_str, end):
        end += 1

    if end > 0:
        if "/" in ing_str[:end]:
            amount = parse_fraction(ing_str[:end])
        else:
            amount = float(ing_str[:end].replace(",", "."))
    else:
        amount = parse_fraction(ing_str[0])
        end += 1
        did_check_frac = True
    if end < len(ing_str):
        if did_check_frac:
            unit = ing_str[end:]
        else:
            try:
                amount += parse_fraction(ing_str[end])

                unit_end = end + 1
                unit = ing_str[unit_end:]
            except ValueError:
                unit = ing_str[end:]

    # i dont know any unit that starts with ( or - so its likely an alternative like 1L (500ml) Water or 2-3
    if unit.startswith("(") or unit.startswith("-"):
        unit = ""
        note = ing_str

    return amount, unit, note


def parse_ingredient_with_comma(tokens) -> Tuple[str, str]:
    ingredient = ""
    note = ""
    start = 0
    # search for first occurrence of an argument ending in a comma
    while start < len(tokens) and not tokens[start].endswith(","):
        start += 1
    if start == len(tokens):
        # no token ending in a comma found -> use everything as ingredient
        ingredient = " ".join(tokens)
    else:
        ingredient = " ".join(tokens[: start + 1])[:-1]

        note_end = start + 1
        note = " ".join(tokens[note_end:])
    return ingredient, note


def parse_ingredient(tokens) -> Tuple[str, str]:
    ingredient = ""
    note = ""
    if tokens[-1].endswith(")"):
        # Check if the matching opening bracket is in the same token
        if (not tokens[-1].startswith("(")) and ("(" in tokens[-1]):
            return parse_ingredient_with_comma(tokens)
        # last argument ends with closing bracket -> look for opening bracket
        start = len(tokens) - 1
        while not tokens[start].startswith("(") and start != 0:
            start -= 1
        if start == 0:
            # the whole list is wrapped in brackets -> assume it is an error (e.g. assumed first argument was the unit)  # noqa: E501
            raise ValueError
        elif start < 0:
            # no opening bracket anywhere -> just ignore the last bracket
            ingredient, note = parse_ingredient_with_comma(tokens)
        else:
            # opening bracket found -> split in ingredient and note, remove brackets from note  # noqa: E501
            note = " ".join(tokens[start:])[1:-1]
            ingredient = " ".join(tokens[:start])
    else:
        ingredient, note = parse_ingredient_with_comma(tokens)
    return ingredient, note


def parse(ing_str) -> BruteParsedIngredient:
    amount = 0
    unit = ""
    ingredient = ""
    note = ""
    unit_note = ""

    ing_str = move_parens_to_end(ing_str)

    tokens = ing_str.split()

    # Early return if the ingrdient is a single token and therefore has no other properties
    if len(tokens) == 1:
        ingredient = tokens[0]
        # TODO Refactor to expect BFP to be returned instead of Tuple
        return BruteParsedIngredient(food=ingredient, note=note, amount=amount, unit=unit)

    try:
        # try to parse first argument as amount
        amount, unit, unit_note = parse_amount(tokens[0])
        # only try to parse second argument as amount if there are at least
        # three arguments if it already has a unit there can't be
        # a fraction for the amount
        if len(tokens) > 2:
            try:
                if unit != "":
                    # a unit is already found, no need to try the second argument for a fraction
                    # probably not the best method to do it, but I didn't want to make an if check and paste the exact same thing in the else as already is in the except  # noqa: E501
                    raise ValueError
                # try to parse second argument as amount and add that, in case of '2 1/2' or '2 ½'
                amount += parse_fraction(tokens[1])
                # assume that units can't end with a comma
                if len(tokens) > 3 and not tokens[2].endswith(","):
                    # try to use third argument as unit and everything else as ingredient, use everything as ingredient if it fails  # noqa: E501
                    try:
                        ingredient, note = parse_ingredient(tokens[3:])
                        unit = tokens[2]
                    except ValueError:
                        ingredient, note = parse_ingredient(tokens[2:])
                else:
                    ingredient, note = parse_ingredient(tokens[2:])
            except ValueError:
                # assume that units can't end with a comma
                if not tokens[1].endswith(","):
                    # try to use second argument as unit and everything else as ingredient, use everything as ingredient if it fails  # noqa: E501
                    try:
                        ingredient, note = parse_ingredient(tokens[2:])
                        if unit == "":
                            unit = tokens[1]
                        else:
                            note = tokens[1]
                    except ValueError:
                        ingredient, note = parse_ingredient(tokens[1:])
                else:
                    ingredient, note = parse_ingredient(tokens[1:])
        else:
            # only two arguments, first one is the amount
            # which means this is the ingredient
            ingredient = tokens[1]
    except ValueError:
        try:
            # can't parse first argument as amount
            # -> no unit -> parse everything as ingredient
            ingredient, note = parse_ingredient(tokens)
        except ValueError:
            ingredient = " ".join(tokens[1:])

    if unit_note not in note:
        note += " " + unit_note

    return BruteParsedIngredient(food=ingredient, note=note, amount=amount, unit=unit)
