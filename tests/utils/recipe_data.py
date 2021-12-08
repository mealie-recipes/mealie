from dataclasses import dataclass

from tests import data as test_data


@dataclass
class RecipeSiteTestCase:
    url: str
    html: str
    expected_slug: str
    num_ingredients: int
    num_steps: int
    html_file: str


def get_recipe_test_cases():
    return [
        RecipeSiteTestCase(
            url="https://www.seriouseats.com/taiwanese-three-cup-chicken-san-bei-gi-recipe",
            html="taiwanese-three-cup-chicken-san-bei-gi-recipe.html",
            html_file=test_data.html_taiwanese_three_cup_chicken_san_bei_gi_recipe,
            expected_slug="taiwanese-three-cup-chicken-san-bei-ji-recipe",
            num_ingredients=10,
            num_steps=3,
        ),
        RecipeSiteTestCase(
            url="https://www.rezeptwelt.de/backen-herzhaft-rezepte/schinken-kaese-waffeln-ohne-viel-schnickschnack/4j0bkiig-94d4d-106529-cfcd2-is97x2ml",
            html="schinken-kase-waffeln-ohne-viel-schnickschnack.html",
            html_file=test_data.html_schinken_kase_waffeln_ohne_viel_schnickschnack,
            expected_slug="schinken-kase-waffeln-ohne-viel-schnickschnack",
            num_ingredients=7,
            num_steps=1,  # Malformed JSON Data, can't parse steps just get one string
        ),
        RecipeSiteTestCase(
            url="https://cookpad.com/us/recipes/5544853-sous-vide-smoked-beef-ribs",
            html="sous-vide-smoked-beef-ribs.html",
            html_file=test_data.html_sous_vide_smoked_beef_ribs,
            expected_slug="sous-vide-smoked-beef-ribs",
            num_ingredients=7,
            num_steps=12,
        ),
        RecipeSiteTestCase(
            url="https://www.greatbritishchefs.com/recipes/jam-roly-poly-recipe",
            html="jam-roly-poly-with-custard.html",
            html_file=test_data.html_jam_roly_poly_with_custard,
            expected_slug="jam-roly-poly-with-custard",
            num_ingredients=13,
            num_steps=9,
        ),
        RecipeSiteTestCase(
            url="https://recipes.anovaculinary.com/recipe/sous-vide-shrimp",
            html="sous-vide-shrimp.html",
            html_file=test_data.html_sous_vide_shrimp,
            expected_slug="sous-vide-shrimp",
            num_ingredients=5,
            num_steps=0,
        ),
        RecipeSiteTestCase(
            url="https://www.bonappetit.com/recipe/detroit-style-pepperoni-pizza",
            html="detroit-style-pepperoni-pizza.html",
            html_file=test_data.html_detroit_style_pepperoni_pizza,
            expected_slug="detroit-style-pepperoni-pizza",
            num_ingredients=8,
            num_steps=5,
        ),
    ]


def get_raw_recipe():
    return {
        "name": "Banana Bread",
        "description": "From Angie's mom",
        "image": "banana-bread.jpg",
        "recipeYield": "",
        "recipeIngredient": [
            "4 bananas",
            "1/2 cup butter",
            "1/2 cup sugar",
            "2 eggs",
            "2 cups flour",
            "1/2 tsp baking soda",
            "1 tsp baking powder",
            "pinch salt",
            "1/4 cup nuts (we like pecans)",
        ],
        "recipeInstructions": [
            {
                "@type": "Beat the eggs, then cream with the butter and sugar",
                "text": "Beat the eggs, then cream with the butter and sugar",
            },
            {
                "@type": "Mix in bananas, then flour, baking soda/powder, salt, and nuts",
                "text": "Mix in bananas, then flour, baking soda/powder, salt, and nuts",
            },
            {
                "@type": "Add to greased and floured pan",
                "text": "Add to greased and floured pan",
            },
            {
                "@type": "Bake until brown/cracked, toothpick comes out clean",
                "text": "Bake until brown/cracked, toothpick comes out clean",
            },
        ],
        "totalTime": "None",
        "prepTime": None,
        "tools": ["test_tool"],
        "performTime": None,
        "slug": "",
        "categories": [],
        "tags": ["breakfast", " baking"],
        "dateAdded": "2021-01-12",
        "notes": [],
        "rating": 0,
        "orgURL": None,
        "extras": {},
    }


def get_raw_no_image():
    raw = get_raw_recipe()
    raw["name"] = "Banana Bread No Image"
    raw["image"] = ""
    return raw
