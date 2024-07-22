import json
import random
import string
import time
from dataclasses import dataclass

import requests
from rich.console import Console
from rich.table import Table

console = Console()


def random_string(length: int) -> str:
    return "".join(random.choice(string.ascii_lowercase) for _ in range(length))


def payload_factory() -> dict:
    return {"name": random_string(15)}


def recipe_data(name: str, slug: str, id: str, userId: str, groupId: str) -> dict:
    return {
        "id": id,
        "userId": userId,
        "groupId": groupId,
        "name": name,
        "slug": slug,
        "image": "tNRG",
        "recipeYield": "9 servings",
        "totalTime": "33 Minutes",
        "prepTime": "20 Minutes",
        "cookTime": None,
        "performTime": "13 Minutes",
        "description": "These Levain Bakery-Style Peanut Butter Cookies are the ULTIMATE for serious PB lovers! Supremely thick and chewy with gooey centers and a soft texture, they're packed with peanut butter flavor and Reese's Pieces for the most amazing cookie ever!",
        "recipeCategory": [],
        "tags": [],
        "tools": [],
        "rating": None,
        "orgURL": "https://thedomesticrebel.com/2021/04/28/levain-bakery-style-ultimate-peanut-butter-cookies/",
        "recipeIngredient": [
            {
                "title": None,
                "note": "1 cup unsalted butter, cut into cubes",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "ea3b6702-9532-4fbc-a40b-f99917831c26",
            },
            {
                "title": None,
                "note": "1 cup light brown sugar",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "c5bbfefb-1e23-4ffd-af88-c0363a0fae82",
            },
            {
                "title": None,
                "note": "1/2 cup granulated white sugar",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "034f481b-c426-4a17-b983-5aea9be4974b",
            },
            {
                "title": None,
                "note": "2 large eggs",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "37c1f796-3bdb-4856-859f-dbec90bc27e4",
            },
            {
                "title": None,
                "note": "2 tsp vanilla extract",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "85561ace-f249-401d-834c-e600a2f6280e",
            },
            {
                "title": None,
                "note": "1/2 cup creamy peanut butter",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "ac91bda0-e8a8-491a-976a-ae4e72418cfd",
            },
            {
                "title": None,
                "note": "1 tsp cornstarch",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "4d1256b3-115e-4475-83cd-464fbc304cb0",
            },
            {
                "title": None,
                "note": "1 tsp baking soda",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "64627441-39f9-4ee3-8494-bafe36451d12",
            },
            {
                "title": None,
                "note": "1/2 tsp salt",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "7ae212d0-3cd1-44b0-899e-ec5bd91fd384",
            },
            {
                "title": None,
                "note": "1 cup cake flour",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "06967994-8548-4952-a8cc-16e8db228ebd",
            },
            {
                "title": None,
                "note": "2 cups all-purpose flour",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "bdb33b23-c767-4465-acf8-3b8e79eb5691",
            },
            {
                "title": None,
                "note": "2 cups peanut butter chips",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "12ba0af8-affd-4fb2-9cca-6f1b3e8d3aef",
            },
            {
                "title": None,
                "note": "1½ cups Reese's Pieces candies",
                "unit": None,
                "food": None,
                "disableAmount": True,
                "quantity": 1,
                "originalText": None,
                "referenceId": "4bdc0598-a3eb-41ee-8af0-4da9348fbfe2",
            },
        ],
        "dateAdded": "2022-09-03",
        "dateUpdated": "2022-09-10T15:18:19.866085",
        "createdAt": "2022-09-03T18:31:17.488118",
        "updatedAt": "2022-09-10T15:18:19.869630",
        "recipeInstructions": [
            {
                "id": "60ae53a3-b3ff-40ee-bae3-89fea0b1c637",
                "title": "",
                "text": "Preheat oven to 410° degrees F. Line 2 baking sheets with parchment paper or silicone liners; set aside.",
                "ingredientReferences": [],
            },
            {
                "id": "4e1c30c2-2e96-4a0a-b750-23c9ea3640f8",
                "title": "",
                "text": "In the bowl of a stand mixer, cream together the cubed butter, brown sugar and granulated sugar with the paddle attachment for 30 seconds on low speed. Increase speed to medium and beat for another 30 seconds, then increase to medium-high speed and beat for another 30 seconds until mixture is creamy and smooth. Beat in the eggs, one at a time, followed by the vanilla extract and peanut butter, scraping down the sides and bottom of the bowl as needed.",
                "ingredientReferences": [],
            },
            {
                "id": "9fb8e2a2-d410-445c-bafc-c059203e6f4b",
                "title": "",
                "text": "Add in the cornstarch, baking soda, salt, cake flour, and all-purpose flour and mix on low speed until just combined. Fold in the peanut butter chips and Reese's Pieces candies by hand until fully incorporated. Chill the dough uncovered in the fridge for 15 minutes.",
                "ingredientReferences": [],
            },
            {
                "id": "1ceb9aa4-49f7-4d4a-996f-3c715eb74642",
                "title": "",
                "text": 'Using a digital kitchen scale for accuracy, weigh out 6 ounces of cookie dough in a loose, rough textured ball. I like to make my cookie dough balls kind of tall as well. You do not want the dough balls to be smooth and compacted. Place on the baking sheet. Repeat with remaining dough balls, staggering on the baking sheet at least 3" apart from one another, and only placing 4 dough balls per baking sheet.',
                "ingredientReferences": [],
            },
            {
                "id": "591993fc-72bb-4091-8a12-84640c523fc1",
                "title": "",
                "text": "Bake one baking sheet at a time in the center rack of the oven for 10-13 minutes or until the tops are light golden brown and the exterior is dry and dull looking. Centers will be slightly underdone and gooey; this is okay and the cookies will finish cooking some once removed from the oven. Let stand on the baking sheets for at least 30 minutes before serving; the cookies are very delicate and fragile once removed from the oven and need time to set before being moved. Keep remaining dough refrigerated while other cookies bake.",
                "ingredientReferences": [],
            },
        ],
        "nutrition": {
            "calories": None,
            "fatContent": None,
            "proteinContent": None,
            "carbohydrateContent": None,
            "fiberContent": None,
            "sodiumContent": None,
            "sugarContent": None,
        },
        "settings": {
            "public": True,
            "showNutrition": False,
            "showAssets": False,
            "landscapeView": False,
            "disableComments": False,
            "disableAmount": True,
            "locked": False,
        },
        "assets": [],
        "notes": [],
        "extras": {},
        "comments": [],
    }


def login(username="changeme@example.com", password="MyPassword"):
    payload = {"username": username, "password": password}
    r = requests.post("http://localhost:9000/api/auth/token", payload)

    # Bearer
    token = json.loads(r.text).get("access_token")
    return {"Authorization": f"Bearer {token}"}


def populate_data(token):
    for _ in range(300):
        payload = payload_factory()
        r = requests.post("http://localhost:9000/api/recipes", json=payload, headers=token)

        if r.status_code != 201:
            console.print(f"Error: {r.status_code}")
            console.print(r.text)
            exit()

        recipe_json = requests.get(f"http://localhost:9000/api/recipes/{payload['name']}", headers=token)

        if recipe_json.status_code != 200:
            console.print(f"Error: {recipe_json.status_code}")
            console.print(recipe_json.text)
            exit()

        recipe = json.loads(recipe_json.text)
        update_data = recipe_data(recipe["name"], recipe["slug"], recipe["id"], recipe["userId"], recipe["groupId"])

        r = requests.put(f"http://localhost:9000/api/recipes/{update_data['slug']}", json=update_data, headers=token)
        if r.status_code != 200:
            console.print(f"Error: {r.status_code}")
            console.print(r.text)
            exit()


@dataclass(slots=True)
class Result:
    recipes: int
    time: float


def time_request(url, headers) -> Result:
    start = time.time()
    r = requests.get(url, headers=headers)
    end = time.time()

    return Result(len(r.json()["items"]), end - start)


def main():
    token = login()
    # populate_data(token)

    results: list[Result] = []

    for _ in range(10):
        result = time_request("http://localhost:9000/api/recipes?perPage=-1&page=1&loadFood=true", token)
        results.append(result)

    min, max, average = 99, 0, 0

    for result in results:
        if result.time < min:
            min = result.time

        if result.time > max:
            max = result.time

        average += result.time

    tbl1 = Table(title="Requests")

    tbl1.add_column("Recipes", justify="right", style="cyan", no_wrap=True)
    tbl1.add_column("Time", justify="right", style="magenta")

    for result in results:
        tbl1.add_row(
            str(result.recipes),
            str(result.time),
        )

    tbl2 = Table(title="Summary")

    tbl2.add_column("Min", justify="right", style="green")
    tbl2.add_column("Max", justify="right", style="green")
    tbl2.add_column("Average", justify="right", style="green")

    tbl2.add_row(
        str(round(min * 1000)) + "ms",
        str(round(max * 1000)) + "ms",
        str(round((average / len(results)) * 1000)) + "ms",
    )

    console = Console()
    console.print(tbl1)
    console.print(tbl2)

    # Best Time 289 / 405/ 247


if __name__ == "__main__":
    main()
