from enum import Enum


class RecipeImageTypes(str, Enum):
    original = "original.webp"
    min = "min-original.webp"
    tiny = "tiny-original.webp"
