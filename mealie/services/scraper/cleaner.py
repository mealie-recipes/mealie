import html
import json
import re
from datetime import datetime, timedelta
from typing import List

from slugify import slugify


def clean(recipe_data: dict, url=None) -> dict:
    """Main entrypoint to clean a recipe extracted from the web
    and format the data into an accectable format for the database

    Args:
        recipe_data (dict): raw recipe dicitonary

    Returns:
        dict: cleaned recipe dictionary
    """
    recipe_data["description"] = clean_string(recipe_data.get("description", ""))

    # Times
    recipe_data["prepTime"] = clean_time(recipe_data.get("prepTime"))
    recipe_data["performTime"] = clean_time(recipe_data.get("performTime"))
    recipe_data["totalTime"] = clean_time(recipe_data.get("totalTime"))
    recipe_data["recipeCategory"] = category(recipe_data.get("recipeCategory", []))

    recipe_data["recipeYield"] = yield_amount(recipe_data.get("recipeYield"))
    recipe_data["recipeIngredient"] = ingredient(recipe_data.get("recipeIngredient"))
    recipe_data["recipeInstructions"] = instructions(recipe_data.get("recipeInstructions"))
    recipe_data["image"] = image(recipe_data.get("image"))
    recipe_data["slug"] = slugify(recipe_data.get("name"))
    recipe_data["orgURL"] = url

    return recipe_data


def clean_string(text: str) -> str:
    if isinstance(text, list):
        text = text[0]

    print(type(text))

    if text == "" or text is None:
        return ""

    print(text)

    cleaned_text = html.unescape(text)
    cleaned_text = re.sub("<[^<]+?>", "", cleaned_text)
    cleaned_text = re.sub(" +", " ", cleaned_text)
    cleaned_text = re.sub("</p>", "\n", cleaned_text)
    cleaned_text = re.sub(r"\n\s*\n", "\n\n", cleaned_text)
    cleaned_text = cleaned_text.replace("\xa0", " ").replace("\t", " ").strip()
    return cleaned_text


def category(category: str):
    if isinstance(category, str) and category != "":
        return [category]
    else:
        return []


def clean_html(raw_html):
    cleanr = re.compile("<.*?>")
    return re.sub(cleanr, "", raw_html)


def image(image=None) -> str:
    if not image:
        return "no image"
    if isinstance(image, list):
        return image[0]
    elif isinstance(image, dict):
        return image["url"]
    elif isinstance(image, str):
        return image
    else:
        raise Exception(f"Unrecognised image URL format: {image}")


def instructions(instructions) -> List[dict]:
    try:
        instructions = json.loads(instructions)
    except Exception:
        pass

    if not instructions:
        return []

    # Dictionary (Keys: step number strings, Values: the instructions)
    if isinstance(instructions, dict):
        instructions = list(instructions.values())

    if isinstance(instructions, list) and isinstance(instructions[0], list):
        instructions = instructions[0]

    # One long string split by (possibly multiple) new lines
    if isinstance(instructions, str):
        return [{"text": _instruction(line)} for line in instructions.splitlines() if line]

    # Plain strings in a list
    elif isinstance(instructions, list) and isinstance(instructions[0], str):
        return [{"text": _instruction(step)} for step in instructions]

    # Dictionaries (let's assume it's a HowToStep) in a list
    elif isinstance(instructions, list) and isinstance(instructions[0], dict):
        # Try List of Dictionary without "@type" or "type"
        if not instructions[0].get("@type", False) and not instructions[0].get("type", False):
            return [{"text": _instruction(step["text"])} for step in instructions]

        try:
            # If HowToStep is under HowToSection
            sectionSteps = []
            for step in instructions:
                if step["@type"] == "HowToSection":
                    [sectionSteps.append(item) for item in step["itemListElement"]]

            if len(sectionSteps) > 0:
                return [{"text": _instruction(step["text"])} for step in sectionSteps if step["@type"] == "HowToStep"]

            return [{"text": _instruction(step["text"])} for step in instructions if step["@type"] == "HowToStep"]
        except Exception as e:
            print(e)
            # Not "@type", try "type"
            try:
                return [
                    {"text": _instruction(step["properties"]["text"])}
                    for step in instructions
                    if step["type"].find("HowToStep") > -1
                ]
            except Exception:
                pass

    else:
        raise Exception(f"Unrecognised instruction format: {instructions}")


def _instruction(line) -> str:
    clean_line = clean_string(line.strip())
    # Some sites erroneously escape their strings on multiple levels
    while not clean_line == (clean_line := clean_string(clean_line)):
        pass
    return clean_line


def ingredient(ingredients: list) -> str:
    if ingredients:
        return [clean_string(ing) for ing in ingredients]
    else:
        return []


def yield_amount(yld) -> str:
    if isinstance(yld, list):
        return yld[-1]
    else:
        return yld


def clean_time(time_entry):
    if time_entry is None:
        return None
    elif isinstance(time_entry, timedelta):
        pretty_print_timedelta(time_entry)
    elif isinstance(time_entry, datetime):
        print(time_entry)
    elif isinstance(time_entry, str):
        if re.match("PT.*H.*M", time_entry):
            time_delta_object = parse_duration(time_entry)
            return pretty_print_timedelta(time_delta_object)
    else:
        return str(time_entry)


# ! TODO: Cleanup Code Below


def parse_duration(iso_duration):
    """Parses an ISO 8601 duration string into a datetime.timedelta instance.
    Args:
        iso_duration: an ISO 8601 duration string.
    Returns:
        a datetime.timedelta instance
    """
    m = re.match(r"^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:.\d+)?)S)?$", iso_duration)
    if m is None:
        raise ValueError("invalid ISO 8601 duration string")

    days = 0
    hours = 0
    minutes = 0
    seconds = 0.0

    # Years and months are not being utilized here, as there is not enough
    # information provided to determine which year and which month.
    # Python's time_delta class stores durations as days, seconds and
    # microseconds internally, and therefore we'd have to
    # convert parsed years and months to specific number of days.

    if m[3]:
        days = int(m[3])
    if m[4]:
        hours = int(m[4])
    if m[5]:
        minutes = int(m[5])
    if m[6]:
        seconds = float(m[6])

    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def pretty_print_timedelta(t, max_components=None, max_decimal_places=2):
    """
    Print a pretty string for a timedelta.
    For example datetime.timedelta(days=2, seconds=17280) will be printed as '2 days, 4 hours, 48 minutes'. Setting max_components to e.g. 1 will change this to '2.2 days', where the
    number of decimal points can also be set.
    """
    time_scales = [
        timedelta(days=365),
        timedelta(days=1),
        timedelta(hours=1),
        timedelta(minutes=1),
        timedelta(seconds=1),
        timedelta(microseconds=1000),
        timedelta(microseconds=1),
    ]
    time_scale_names_dict = {
        timedelta(days=365): "year",
        timedelta(days=1): "day",
        timedelta(hours=1): "Hour",
        timedelta(minutes=1): "Minute",
        timedelta(seconds=1): "Second",
        timedelta(microseconds=1000): "millisecond",
        timedelta(microseconds=1): "microsecond",
    }
    count = 0
    txt = ""
    first = True
    for scale in time_scales:
        if t >= scale:
            count += 1
            n = t / scale if count == max_components else int(t / scale)
            t -= n * scale

            n_txt = str(round(n, max_decimal_places))
            if n_txt[-2:] == ".0":
                n_txt = n_txt[:-2]
            txt += "{}{} {}{}".format(
                "" if first else " ",
                n_txt,
                time_scale_names_dict[scale],
                "s" if n > 1 else "",
            )
            if first:
                first = False

    if len(txt) == 0:
        txt = "none"
    return txt
