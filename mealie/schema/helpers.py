from fastapi_camelcase import CamelModel


class RecipeSlug(CamelModel):
    slug: str
