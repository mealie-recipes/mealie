import contextlib
import functools
import html
import json
import operator
import re
import typing
from datetime import datetime, timedelta

from slugify import slugify

from mealie.core.root_logger import get_logger
from mealie.lang.providers import Translator, get_all_translations
from mealie.schema.recipe.recipe import Recipe
from mealie.services.parser_services.parser_utils import extract_quantity_from_string

logger = get_logger("recipe-scraper")


MATCH_DIGITS = re.compile(r"\d+([.,]\d+)?")
""" Allow for commas as decimals (common in Europe) """

MATCH_ISO_STR = re.compile(
    r"^P((\d+)Y)?((\d+)M)?((?P<days>\d+)D)?" r"T((?P<hours>\d+)H)?((?P<minutes>\d+)M)?((?P<seconds>\d+(?:\.\d+)?)S)?$",
)
""" Match Duration Strings """

MATCH_HTML_TAGS = re.compile(r"<[^<]+?>")
""" Matches HTML tags `<p>Text</p>` -> `Text` """

MATCH_MULTI_SPACE = re.compile(r" +")
""" Matches multiple spaces `Hello    World` -> `Hello World` """

MATCH_ERRONEOUS_WHITE_SPACE = re.compile(r"\n\s*\n")
""" Matches multiple new lines and removes erroneous white space """


def clean(recipe_data: Recipe | dict, translator: Translator, url=None) -> Recipe:
    """Main entrypoint to clean a recipe extracted from the web
    and format the data into an accectable format for the database

    Args:
        recipe_data (dict): raw recipe or recipe dictionary

    Returns:
        dict: cleaned recipe dictionary
    """
    if not isinstance(recipe_data, dict):
        # format the recipe like a scraped dictionary
        recipe_data_dict = recipe_data.model_dump(by_alias=True)
        recipe_data_dict["recipeIngredient"] = [ing.display for ing in recipe_data.recipe_ingredient]

        recipe_data = recipe_data_dict

    recipe_data["slug"] = slugify(recipe_data.get("name", ""))
    recipe_data["description"] = clean_string(recipe_data.get("description", ""))

    recipe_data["prepTime"] = clean_time(recipe_data.get("prepTime"), translator)
    recipe_data["performTime"] = clean_time(recipe_data.get("performTime"), translator)
    recipe_data["totalTime"] = clean_time(recipe_data.get("totalTime"), translator)

    recipe_data["recipeServings"], recipe_data["recipeYieldQuantity"], recipe_data["recipeYield"] = clean_yield(
        recipe_data.get("recipeYield")
    )
    recipe_data["recipeCategory"] = clean_categories(recipe_data.get("recipeCategory", []))
    recipe_data["recipeIngredient"] = clean_ingredients(recipe_data.get("recipeIngredient", []))
    recipe_data["recipeInstructions"] = clean_instructions(recipe_data.get("recipeInstructions", []))

    recipe_data["image"] = clean_image(recipe_data.get("image"))[0]
    recipe_data["orgURL"] = url or recipe_data.get("orgURL")
    recipe_data["notes"] = clean_notes(recipe_data.get("notes"))
    recipe_data["rating"] = clean_int(recipe_data.get("rating"))

    return Recipe(**recipe_data)


def clean_string(text: str | list | int) -> str:
    """Cleans a string of HTML tags and extra white space"""
    if not isinstance(text, str):
        if isinstance(text, list):
            text = text[0]

        if isinstance(text, int):
            text = str(text)

    if not text:
        return ""

    text = typing.cast(str, text)  # at this point we know text is a string

    cleaned_text = html.unescape(text)
    cleaned_text = MATCH_HTML_TAGS.sub("", cleaned_text)
    cleaned_text = MATCH_MULTI_SPACE.sub(" ", cleaned_text)
    cleaned_text = MATCH_ERRONEOUS_WHITE_SPACE.sub("\n\n", cleaned_text)

    cleaned_text = cleaned_text.replace("</p>", "\n").replace("\xa0", " ").replace("\t", " ").strip()
    return cleaned_text


def clean_image(image: str | list | dict | None = None, default: str = "no image") -> list[str]:
    """
    image attempts to parse the image field from a recipe and return a string. Currenty

    Supported Structures:
        - `https://example.com` - A string
        - `{ "url": "https://example.com" }` - A dictionary with a `url` key
        - `["https://example.com"]` - A list of strings
        - `[{ "url": "https://example.com" }]` - A list of dictionaries with a `url` key

    Raises:
        TypeError: If the image field is not a supported type a TypeError is raised.

    Returns:
        list[str]: list of urls, or [default] if input is empty
    """
    if not image:
        return [default]

    match image:
        case str(image):
            return [image]
        case [str(_), *_]:
            # Only return non-null strings in list
            return [x for x in image if x]
        case [{"url": str(_)}, *_]:
            return [x["url"] for x in image if "url" in x]
        case {"url": str(image)}:
            return [image]
        case [{"@id": str(_)}, *_]:
            return [x["@id"] for x in image if "@id" in x]
        case _:
            logger.exception(f"Unexpected type for image: {type(image)}, {image}")
            return [default]


def clean_instructions(steps_object: list | dict | str, default: list | None = None) -> list[dict]:
    """
    instructions attempts to parse the instructions field from a recipe and return a list of
    dictionaries. See match statement for supported types and structures

    Raises:
        TypeError: If the instructions field is not a supported type a TypeError is raised.

    Returns:
        list[dict]: An ordered list of dictionaries with the keys `text`
    """
    if not steps_object:
        return default or []

    match steps_object:
        case [{"text": str()}]:  # Base Case
            return steps_object
        case [{"text": str()}, *_]:
            # The is the most common case. Most other operations eventually resolve to this
            # match case before being converted to a list of instructions
            #
            # [
            #   {"text": "Instruction A"},
            #   {"text": "Instruction B"},
            # ]
            #
            return [
                {"text": _sanitize_instruction_text(instruction["text"])}
                for instruction in steps_object
                if "text" in instruction and instruction["text"].strip()
            ]
        case {0: {"text": str()}} | {"0": {"text": str()}} | {1: {"text": str()}} | {"1": {"text": str()}}:
            # Some recipes have a dict with a string key representing the index, unsure if these can
            # be an int or not so we match against both. Additionally, we match against both 0 and 1 indexed
            # list like dicts.
            #
            # {
            #     "0": {"text": "Instruction A"},
            #     "1": {"text": "Instruction B"},
            # }
            #
            steps_object = typing.cast(dict, steps_object)
            return clean_instructions(list(steps_object.values()))
        case str(step_as_str):
            # Strings are weird, some sites return a single string with newlines
            # others returns a json string for some reasons
            #
            # "Instruction A\nInstruction B\nInstruction C"
            # '{"0": {"text": "Instruction A"}, "1": {"text": "Instruction B"}, "2": {"text": "Instruction C"}}'
            #
            if step_as_str.startswith("[") or step_as_str.startswith("{"):
                try:
                    return clean_instructions(json.loads(step_as_str))
                except json.JSONDecodeError:
                    pass
            return [
                {"text": _sanitize_instruction_text(instruction)}
                for instruction in step_as_str.splitlines()
                if instruction.strip()
            ]
        case [str(), *_]:
            # Assume list of strings is a valid list of instructions
            #
            # [
            #   "Instruction A",
            #   "Instruction B",
            # ]
            #
            return [
                {"text": _sanitize_instruction_text(instruction)} for instruction in steps_object if instruction.strip()
            ]
        case [{"@type": "HowToSection"}, *_] | [{"type": "HowToSection"}, *_]:
            # HowToSections should have the following layout,
            # {
            #  "@type": "HowToSection",
            #  "itemListElement": [
            #    {
            #      "@type": "HowToStep",
            #      "text": "Instruction A"
            #    },
            # }
            #
            steps_object = typing.cast(list[dict[str, str]], steps_object)
            return clean_instructions(
                functools.reduce(
                    operator.concat,  # type: ignore
                    [x["itemListElement"] for x in steps_object],
                    [],
                )
            )
        case _:
            raise TypeError(f"Unexpected type for instructions: {type(steps_object)}, {steps_object}")


def _sanitize_instruction_text(line: str | dict) -> str:
    """
    _sanitize_instructions_text does some basic checking if the value is a string or dictionary
    and returns the value of the `text` key if it is a dictionary. The returned string is passed through the
    `clean_string` function to remove any html tags and extra whitespace in a loop until the string
    is stable.

    Calling `clean_string` in a loop is necessary because some sites return a string with erroneously escaped
    html tags or markup.
    """
    if isinstance(line, dict):
        # Some Recipes dotnot adhear to schema
        try:
            line = line["text"]
        except Exception:
            line = ""

    if not line:
        return ""

    line = typing.cast(str, line)
    clean_line = clean_string(line.strip())

    while not clean_line == (clean_line := clean_string(clean_line)):
        pass

    return clean_line


def clean_ingredients(ingredients: list | str | None, default: list | None = None) -> list[str | dict]:
    """
    ingredient attempts to parse the ingredients field from a recipe and return a list of

    Supported Structures:
        - `["1 cup flour"]` - A list of strings
        - `"1 cup flour"` - A string
        - `None` - returns an empty list

    Raises:
        TypeError: If the ingredients field is not a supported type a TypeError is raised.
    """
    match ingredients:
        case None:
            return default or []
        case list(ingredients):
            cleaned_ingredients: list[str | dict] = []
            for ing in ingredients:
                if isinstance(ing, dict):
                    cleaned_ingredients.append({clean_string(k): clean_string(v) for k, v in ing.items()})
                else:
                    cleaned_ingredients.append(clean_string(ing))
            return cleaned_ingredients
        case [str()]:
            return [clean_string(ingredient) for ingredient in ingredients]
        case str(ingredients):
            return [clean_string(ingredient) for ingredient in ingredients.splitlines() if ingredient.strip()]
        case _:
            raise TypeError(f"Unexpected type for ingredients: {type(ingredients)}, {ingredients}")


def clean_int(val: str | int | None, min: int | None = None, max: int | None = None):
    if val is None or isinstance(val, int):
        return val

    filtered_val = "".join(c for c in val if c.isnumeric())
    if not filtered_val:
        return None

    val = int(filtered_val)
    if min is None or max is None:
        return val

    if not (min <= val <= max):
        return None

    return val


def clean_notes(notes: typing.Any) -> list[dict] | None:
    if not isinstance(notes, list):
        return None

    parsed_notes: list[dict] = []
    for note in notes:
        if not isinstance(note, str | dict):
            continue

        if isinstance(note, dict):
            if "text" not in note:
                continue

            if "title" not in note:
                note["title"] = ""

            parsed_notes.append(note)
            continue

        parsed_notes.append({"title": "", "text": note})

    return parsed_notes


@functools.lru_cache
def _get_servings_options() -> set[str]:
    options: set[str] = set()
    for key in [
        "recipe.servings-text.makes",
        "recipe.servings-text.serves",
        "recipe.servings-text.serving",
        "recipe.servings-text.servings",
        "recipe.servings-text.yield",
        "recipe.servings-text.yields",
    ]:
        options.update([t.strip().lower() for t in get_all_translations(key).values()])

    return options


def _is_serving_string(txt: str) -> bool:
    txt = txt.strip().lower()
    for option in _get_servings_options():
        if option in txt.strip().lower():
            return True
    return False


def clean_yield(yields: str | list[str] | None) -> tuple[float, float, str]:
    """
    yield_amount attemps to parse out the yield amount from a recipe.

    Supported Structures:
        - `"4 servings"` - returns the string unmodified
        - `["4 servings", "4 Pies"]` - returns the last value

    Returns:
        float: The servings, if it can be parsed else 0
        float: The yield quantity, if it can be parsed else 0
        str: The yield amount, if it can be parsed else an empty string
    """
    servings_qty: float = 0
    yld_qty: float = 0
    yld_str = ""

    if not yields:
        return servings_qty, yld_qty, yld_str

    if not isinstance(yields, list):
        yields = [yields]

    for yld in yields:
        if not yld:
            continue
        if not isinstance(yld, str):
            yld = str(yld)

        qty, txt = extract_quantity_from_string(yld)
        if qty and _is_serving_string(yld):
            servings_qty = qty
        else:
            yld_qty = qty
            yld_str = txt

    return servings_qty, yld_qty, yld_str


def clean_time(time_entry: str | timedelta | None, translator: Translator) -> None | str:
    """_summary_

    Supported Structures:
        - `None` - returns None
        - `"PT1H"` - returns "1 hour"
        - `"PT1H30M"` - returns "1 hour 30 minutes"
        - `timedelta(hours=1, minutes=30)` - returns "1 hour 30 minutes"
        - `{"minValue": "PT1H30M"}` - returns "1 hour 30 minutes"

    Raises:
        TypeError: if the type is not supported a TypeError is raised

    Returns:
        None | str: None if the time_entry is None, otherwise a string representing the time
    """
    if not time_entry:
        return None

    match time_entry:
        case str(time_entry):
            if not time_entry.strip():
                return None

            try:
                time_delta_instructionsect = parse_duration(time_entry)
                return pretty_print_timedelta(time_delta_instructionsect, translator)
            except ValueError:
                return str(time_entry)
        case timedelta():
            return pretty_print_timedelta(time_entry, translator)
        case {"minValue": str(value)}:
            return clean_time(value, translator)
        case [str(), *_]:
            return clean_time(time_entry[0], translator)
        case datetime():
            # TODO: Not sure what to do here
            return str(time_entry)
        case _:
            logger.warning("[SCRAPER] Unexpected type or structure for variable time_entry")
            return None


def parse_duration(iso_duration: str) -> timedelta:
    """
    Parses an ISO 8601 duration string into a datetime.timedelta instance.

    Args:
        iso_duration: an ISO 8601 duration string.

    Raises:
        ValueError: if the input string is not a valid ISO 8601 duration string.
    """

    m = MATCH_ISO_STR.match(iso_duration)

    if m is None:
        raise ValueError("invalid ISO 8601 duration string")

    # Years and months are not being utilized here, as there is not enough
    # information provided to determine which year and which month.
    # Python's time_delta class stores durations as days, seconds and
    # microseconds internally, and therefore we'd have to
    # convert parsed years and months to specific number of days.

    times = {"days": 0, "hours": 0, "minutes": 0, "seconds": 0}
    for unit in times.keys():
        if m.group(unit):
            times[unit] = int(float(m.group(unit)))

    return timedelta(**times)


def pretty_print_timedelta(t: timedelta, translator: Translator, max_components=None, max_decimal_places=2):
    """
    Print a pretty string for a timedelta.
    For example datetime.timedelta(days=2, seconds=17280) will be printed as '2 days 4 Hours 48 Minutes'.
    Setting max_components to e.g. 1 will change this to '2.2 days', where the number of decimal
    points can also be set.
    """
    time_scale_translation_keys_dict = {
        timedelta(days=365): "datetime.year",
        timedelta(days=1): "datetime.day",
        timedelta(hours=1): "datetime.hour",
        timedelta(minutes=1): "datetime.minute",
        timedelta(seconds=1): "datetime.second",
        timedelta(microseconds=1000): "datetime.millisecond",
        timedelta(microseconds=1): "datetime.microsecond",
    }
    count = 0
    out_list = []
    for scale, scale_translation_key in time_scale_translation_keys_dict.items():
        if t >= scale:
            count += 1
            n = t / scale if count == max_components else int(t / scale)
            t -= n * scale

            n_txt = str(round(n, max_decimal_places))
            if n_txt[-2:] == ".0":
                n_txt = n_txt[:-2]

            scale_value = translator.t(scale_translation_key, count=n)
            out_list.append(f"{n_txt} {scale_value}")

    if out_list == []:
        return "none"
    return " ".join(out_list)


def clean_categories(category: str | list) -> list[str]:
    if not category:
        return []

    match category:
        case str(category):
            if not category.strip():
                return []

            return [category]
        case [str(), *_]:
            return [cat.strip().title() for cat in category if cat.strip()]
        case [{"name": str(), "slug": str()}, *_]:
            # Special case for when we use the cleaner to cleanup a migration.
            #
            # [
            #     { "name": "Dessert", "slug": "dessert"}
            # ]
            #
            return [cat["name"] for cat in category if "name" in cat]
        case _:
            raise TypeError(f"Unexpected type for category: {type(category)}, {category}")


def clean_tags(data: str | list[str]) -> list[str]:
    """
    Gets keywords as a list or natural language list and returns
    them into a list of strings of individual tags
    """
    if not data:
        return []

    match data:
        case [str(), *_]:
            return [tag.strip().title() for tag in data if tag.strip()]
        case str(data):
            return clean_tags(data.split(","))
        case _:
            return []
            # should probably raise exception
            # raise TypeError(f"Unexpected type for tags: {type(data)}, {data}")


def clean_nutrition(nutrition: dict | None) -> dict[str, str]:
    """
    clean_nutrition takes a dictionary of nutrition information and cleans it up
    to be stored in the database. It will remove any keys that are not in the
    list of valid keys

    Assumptionas:
        - All units are supplied in grams, expect sodium and cholesterol which maybe be in milligrams

    Returns:
        dict[str, str]: If the argument is None, or not a dictionary, an empty dictionary is returned
    """
    if not isinstance(nutrition, dict):
        return {}

    output_nutrition = {}
    for key, val in nutrition.items():
        with contextlib.suppress(AttributeError, TypeError):
            if matched_digits := MATCH_DIGITS.search(val):
                output_nutrition[key] = matched_digits.group(0).replace(",", ".")

    for key in ["sodiumContent", "cholesterolContent"]:
        if val := nutrition.get(key, None):
            if isinstance(val, str) and "m" not in val and "g" in val:
                with contextlib.suppress(AttributeError, TypeError):
                    output_nutrition[key] = str(float(output_nutrition[key]) * 1000)

    for key in ["calories"]:
        if val := nutrition.get(key, None):
            if isinstance(val, int | float):
                with contextlib.suppress(AttributeError, TypeError):
                    output_nutrition[key] = str(val)

    return output_nutrition
