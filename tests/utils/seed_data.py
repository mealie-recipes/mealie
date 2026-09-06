from mealie.repos.seed.seeders import IngredientFoodsSeeder, IngredientUnitsSeeder, MultiPurposeLabelSeeder


def seeded_food_names(locale: str) -> set[str]:
    seed_data = IngredientFoodsSeeder.load_file(IngredientFoodsSeeder.get_file(locale))
    return {attributes["name"] for label in seed_data.values() for attributes in label["foods"].values()}


def seeded_unit_names(locale: str) -> set[str]:
    seed_data = IngredientUnitsSeeder.load_file(IngredientUnitsSeeder.get_file(locale))
    return {unit["name"] for unit in seed_data.values()}


def seeded_label_names(locale: str) -> set[str]:
    seed_data = MultiPurposeLabelSeeder.load_file(MultiPurposeLabelSeeder.get_file(locale))
    return set(filter(None, seed_data.keys()))
