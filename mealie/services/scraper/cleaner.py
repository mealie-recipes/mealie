import html
import re
from datetime import datetime
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
        recipe_data["prepTime"] = Cleaner.time(recipe_data.get("prepTime", None))
        recipe_data["performTime"] = Cleaner.time(recipe_data.get("performTime", None))
        recipe_data["totalTime"] = Cleaner.time(recipe_data.get("totalTime", None))
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
        if isinstance(category, str):
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

        return [Cleaner.html(html.unescape(ing)) for ing in ingredients]

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
        elif isinstance(time_entry, datetime):
            print(time_entry)
        else:
            return str(time_entry)
