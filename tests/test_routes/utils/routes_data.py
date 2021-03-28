class RecipeTestData:
    def __init__(self, url, expected_slug) -> None:
        self.url: str = url
        self.expected_slug: str = expected_slug


recipe_test_data = [
    RecipeTestData(
        url="https://www.bonappetit.com/recipe/spinach-thepla-and-vaghareli-dahi",
        expected_slug="thepla-recipe-with-vaghareli-dahi",
    ),
    RecipeTestData(
        url="https://www.bonappetit.com/recipe/classic-coleslaw",
        expected_slug="traditional-coleslaw-recipe",
    ),
]


raw_recipe = {
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

raw_recipe_no_image = {
    "name": "Banana Bread No Image",
    "description": "From Angie's mom",
    "image": "",
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
