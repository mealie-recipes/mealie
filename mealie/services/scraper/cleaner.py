import html
import re
from datetime import datetime, timedelta
from typing import List

from slugify import slugify


class Cleaner:
    """A Namespace for utility function to clean recipe data extracted
    from a url and returns a dictionary that is ready for import into
    the database. Cleaner.clean is the main entrypoint
    """

    @staticmethod
    def clean(recipe_data: dict, url=None) -> dict:
        """Main entrypoint to clean a recipe extracted from the web
        and format the data into an accectable format for the database

        Args:
            recipe_data (dict): raw recipe dicitonary

        Returns:
            dict: cleaned recipe dictionary
        """
        recipe_data["description"] = Cleaner.html(recipe_data.get("description", ""))

        # Times
        recipe_data["prepTime"] = Cleaner.time(recipe_data.get("prepTime"))
        recipe_data["performTime"] = Cleaner.time(recipe_data.get("performTime"))
        recipe_data["totalTime"] = Cleaner.time(recipe_data.get("totalTime"))
        recipe_data["recipeCategory"] = Cleaner.category(recipe_data.get("recipeCategory", []))

        recipe_data["recipeYield"] = Cleaner.yield_amount(recipe_data.get("recipeYield"))
        recipe_data["recipeIngredient"] = Cleaner.ingredient(recipe_data.get("recipeIngredient"))
        recipe_data["recipeInstructions"] = Cleaner.instructions(recipe_data["recipeInstructions"])
        recipe_data["image"] = Cleaner.image(recipe_data.get("image"))
        recipe_data["slug"] = slugify(recipe_data.get("name"))
        recipe_data["orgURL"] = url

        return recipe_data

    @staticmethod
    def category(category: str):
        if isinstance(category, str) and category != "":
            return [category]
        else:
            return []

    @staticmethod
    def html(raw_html):
        cleanr = re.compile("<.*?>")
        return re.sub(cleanr, "", raw_html)

    @staticmethod
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

    @staticmethod
    def instructions(instructions) -> List[dict]:
        if not instructions:
            return []

        # Dictionary (Keys: step number strings, Values: the instructions)
        if isinstance(instructions, dict):                            
           instructions = list(instructions.values())    

        if isinstance(instructions[0], list):
            instructions = instructions[0]

        # One long string split by (possibly multiple) new lines
        if isinstance(instructions, str):
            return [{"text": Cleaner._instruction(line)} for line in instructions.splitlines() if line]

        # Plain strings in a list
        elif isinstance(instructions, list) and isinstance(instructions[0], str):
            return [{"text": Cleaner._instruction(step)} for step in instructions]

        # Dictionaries (let's assume it's a HowToStep) in a list
        elif isinstance(instructions, list) and isinstance(instructions[0], dict):
            # Try List of Dictionary without "@type" or "type"
            if not instructions[0].get("@type", False) and not instructions[0].get("type", False):
                return [{"text": Cleaner._instruction(step["text"])} for step in instructions]

            try:
                # If HowToStep is under HowToSection
                sectionSteps = []
                for step in instructions:
                    if step["@type"] == "HowToSection":
                        [sectionSteps.append(item) for item in step["itemListElement"]]

                if len(sectionSteps) > 0:
                    return [
                        {"text": Cleaner._instruction(step["text"])}
                        for step in sectionSteps
                        if step["@type"] == "HowToStep"
                    ]

                return [
                    {"text": Cleaner._instruction(step["text"])}
                    for step in instructions
                    if step["@type"] == "HowToStep"
                ]
            except Exception as e:
                print(e)
                # Not "@type", try "type"
                try:
                    return [
                        {"text": Cleaner._instruction(step["properties"]["text"])}
                        for step in instructions
                        if step["type"].find("HowToStep") > -1
                    ]
                except:
                    pass

        else:
            raise Exception(f"Unrecognised instruction format: {instructions}")

    @staticmethod
    def _instruction(line) -> str:
        clean_line = Cleaner.html(line.strip())
        # Some sites erroneously escape their strings on multiple levels
        while not clean_line == (clean_line := html.unescape(clean_line)):
            pass
        return clean_line

    @staticmethod
    def ingredient(ingredients: list) -> str:
        if ingredients:
            return [Cleaner.html(html.unescape(ing)) for ing in ingredients]
        else:
            return []

    @staticmethod
    def yield_amount(yld) -> str:
        if isinstance(yld, list):
            return yld[-1]
        else:
            return yld

    @staticmethod
    def time(time_entry):
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
