import requests
import json

POST_URL = "http://localhost:9921/api/recipe/create-url"
URL_LIST = [
    "https://www.bonappetit.com/recipe/hallacas"
    "https://www.bonappetit.com/recipe/oat-and-pecan-brittle-cookies",
    "https://www.bonappetit.com/recipe/tequila-beer-and-citrus-cocktail",
    "https://www.bonappetit.com/recipe/corn-and-crab-beignets-with-yaji-aioli",
    "https://www.bonappetit.com/recipe/nan-e-berenji",
    "https://www.bonappetit.com/recipe/ginger-citrus-cookies",
    "https://www.bonappetit.com/recipe/chocolate-pizzettes-cookies",
    "https://www.bonappetit.com/recipe/swedish-glogg",
    "https://www.bonappetit.com/recipe/roasted-beets-with-dukkah-and-sage",
    "https://www.bonappetit.com/recipe/collard-greens-salad-with-pickled-fennel-and-coconut"
    "https://www.bonappetit.com/recipe/sparkling-wine-cocktail",
    "https://www.bonappetit.com/recipe/pretzel-and-potato-chip-moon-pies",
    "https://www.bonappetit.com/recipe/coffee-hazlenut-biscotti",
    "https://www.bonappetit.com/recipe/curry-cauliflower-rice",
    "https://www.bonappetit.com/recipe/life-of-the-party-layer-cake",
    "https://www.bonappetit.com/recipe/marranitos-enfiestados",
]


if __name__ == "__main__":
    for url in URL_LIST:
        data = {"url": url}
        data = json.dumps(data)
        try:
            response = requests.post(POST_URL, data)
        except:
            continue
