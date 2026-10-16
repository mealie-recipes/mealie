from mealie.repos.seed.seeders import IngredientFoodsSeeder, IngredientUnitsSeeder, RecipeToolsSeeder


def seeded_food_names(locale: str) -> set[str]:
    seed_data = IngredientFoodsSeeder.load_file(IngredientFoodsSeeder.get_file(locale))
    return {attributes["name"] for label in seed_data.values() for attributes in label["foods"].values()}


def seeded_unit_names(locale: str) -> set[str]:
    seed_data = IngredientUnitsSeeder.load_file(IngredientUnitsSeeder.get_file(locale))
    return {unit["name"] for unit in seed_data.values()}


def seeded_tool_names(locale: str) -> set[str]:
    seed_data = RecipeToolsSeeder.load_file(RecipeToolsSeeder.get_file(locale))
    return {tool["name"] for tool in seed_data.values()}


def seeded_label_names(locale: str) -> set[str]:
    seed_data = IngredientFoodsSeeder.load_file(IngredientFoodsSeeder.get_file(locale))
    return {label["name"] for label in seed_data.values() if label["name"]}
