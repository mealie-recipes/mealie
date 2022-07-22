from fastapi import APIRouter, File

from mealie.routes._base import BaseUserController, controller
from mealie.schema.ocr.ocr import OcrAssetReq, OcrTsvResponse
from mealie.services.ocr.pytesseract import OCR
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.recipe.recipe_service import RecipeService

router = APIRouter()


@controller(router)
class OCRController(BaseUserController):
    @router.post("/", response_model=str)
    def image_to_string(self, file: bytes = File(...)):
        return OCR.image_to_string(file)

    @router.post("/file-to-tsv", response_model=list[OcrTsvResponse])
    def file_to_tsv(self, file: bytes = File(...)):
        tsv = OCR.image_to_tsv(file)
        return OCR.format_tsv_output(tsv)

    @router.post("/asset-to-tsv", response_model=list[OcrTsvResponse])
    def asset_to_tsv(self, req: OcrAssetReq):
        recipe = RecipeService._get_recipe(self, req.recipe_slug)
        data_service = RecipeDataService(recipe.id, recipe.group_id)
        asset_path = data_service.dir_assets.joinpath(req.asset_name)
        file = open(asset_path, "rb")
        tsv = OCR.image_to_tsv(file.read())

        return OCR.format_tsv_output(tsv)
