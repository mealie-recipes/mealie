from mealie.schema._mealie import MealieModel


class OcrTsvResponse(MealieModel):
    level: int = 0
    page_num: int = 0
    block_num: int = 0
    par_num: int = 0
    line_num: int = 0
    word_num: int = 0
    left: int = 0
    top: int = 0
    width: int = 0
    height: int = 0
    conf: float = 0.0
    text: str = ""


class OcrAssetReq(MealieModel):
    recipe_slug: str
    asset_name: str
