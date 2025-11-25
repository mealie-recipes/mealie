from mealie.schema._mealie import MealieModel

class TescoBasketItem(MealieModel):
    url: str
    product_name: str
    total_quantity_needed: float
    unit: str
    pack_size: float
    packs_needed: int
    estimated_cost: float
