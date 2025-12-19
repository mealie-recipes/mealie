import json

import requests

from mealie.schema.recipe.recipe_nutrition import FdcNutritionItem
from mealie.services._base_service import BaseService


class NutritionService(BaseService):
    def fdc(self, fdc_id: str) -> list[FdcNutritionItem]:
        nutrition_items: list[FdcNutritionItem] = []

        if not self.settings.FDC_API_KEY or self.settings.FDC_API_KEY == "":
            self.logger.error("No API Key set for FDC access.")
            return nutrition_items

        response = requests.get(
            f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?api_key={self.settings.FDC_API_KEY}", timeout=10
        )

        if response.status_code == 429:
            self.logger.error("API Key Rate Limit reached/exceeded for FDC API Key.")
            return nutrition_items
        if response.status_code != 200:
            self.logger.error("Error while requesting FDC data.")
            return nutrition_items

        try:
            data = json.loads(response.content)
            for nutrition in data.get("foodNutrients", []):
                nutrition_id = nutrition.get("nutrient", {}).get("id", None)
                amount = nutrition.get("amount", None)
                if nutrition_id is None or amount is None:
                    continue
                nutrition_items.append(FdcNutritionItem(fdc_nutrition_id=nutrition_id, value=amount))
        except json.JSONDecodeError:
            self.logger.error("Error while digesting FDC data.")
        return nutrition_items
