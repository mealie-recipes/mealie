from mealie.schema._mealie import MealieModel


class OcrTsvResponse(MealieModel):
    level: int
    page_num: int
    block_num: int
    par_num: int
    line_num: int
    word_num: int
    left: int
    top: int
    width: int
    height: int
    conf: float
    text: str


class OcrAssetReq(MealieModel):
    recipe_slug: str
    asset_name: str
