import html
import re
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
        recipe_data["totalTime"] = Cleaner.time(recipe_data.get("totalTime"))
        recipe_data["description"] = Cleaner.html(recipe_data.get("description", ""))
        recipe_data["prepTime"] = Cleaner.time(recipe_data.get("prepTime"))
        recipe_data["performTime"] = Cleaner.time(recipe_data.get("performTime"))
        recipe_data["recipeYield"] = Cleaner.yield_amount(
            recipe_data.get("recipeYield")
        )
        recipe_data["recipeIngredient"] = Cleaner.ingredient(
            recipe_data.get("recipeIngredient")
        )
        recipe_data["recipeInstructions"] = Cleaner.instructions(
            recipe_data["recipeInstructions"]
        )
        recipe_data["image"] = Cleaner.image(recipe_data["image"])
        recipe_data["slug"] = slugify(recipe_data["name"])
        recipe_data["orgURL"] = url

        return recipe_data

    @staticmethod
    def html(raw_html):
        cleanr = re.compile("<.*?>")
        cleantext = re.sub(cleanr, "", raw_html)
        return cleantext

    @staticmethod
    def image(image) -> str:
        if type(image) == list:
            return image[0]
        elif type(image) == dict:
            return image["url"]
        elif type(image) == str:
            return image
        else:
            raise Exception(f"Unrecognised image URL format: {image}")

    @staticmethod
    def instructions(instructions) -> List[dict]:
        if not instructions:
            return []

        # One long string split by (possibly multiple) new lines
        if type(instructions) == str:
            return [
                {"text": Cleaner._instruction(line)}
                for line in instructions.splitlines()
                if line
            ]

        # Plain strings in a list
        elif type(instructions) == list and type(instructions[0]) == str:
            return [{"text": Cleaner._instruction(step)} for step in instructions]

        # Dictionaries (let's assume it's a HowToStep) in a list
        elif type(instructions) == list and type(instructions[0]) == dict:
            # Try List of Dictionary without "@type" or "type"
            if not instructions[0].get("@type", False) and not instructions[0].get(
                "type", False
            ):
                return [
                    {"text": Cleaner._instruction(step["text"])}
                    for step in instructions
                ]

            try:
                # If HowToStep is under HowToSection
                sectionSteps = []
                for step in instructions:
                    if step["@type"] == "HowToSection":
                        [sectionSteps.append(item) for item in step["itemListELement"]]

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
        l = Cleaner.html(line.strip())
        # Some sites erroneously escape their strings on multiple levels
        while not l == (l := html.unescape(l)):
            pass
        return l

    @staticmethod
    def ingredient(ingredients: list) -> str:

        return [Cleaner.html(html.unescape(ing)) for ing in ingredients]

    @staticmethod
    def yield_amount(yld) -> str:
        if type(yld) == list:
            return yld[-1]
        else:
            return yld

    @staticmethod
    def time(time_entry) -> str:
        if type(time_entry) == type(None):
            return None
        elif type(time_entry) != str:
            return str(time_entry)
