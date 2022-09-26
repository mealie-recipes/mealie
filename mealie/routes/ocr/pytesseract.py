from fastapi import APIRouter, File

from mealie.routes._base import BaseUserController, controller
from mealie.schema.ocr.ocr import OcrAssetReq, OcrTsvResponse
from mealie.services.ocr.pytesseract import OcrService
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.recipe.recipe_service import RecipeService

router = APIRouter()


@controller(router)
class OCRController(BaseUserController):
    def __init__(self):
        self.ocr_service = OcrService()

    @router.post("/", response_model=str)
    def image_to_string(self, file: bytes = File(...)):
        return self.ocr_service.image_to_string(file)

    @router.post("/file-to-tsv", response_model=list[OcrTsvResponse])
    def file_to_tsv(self, file: bytes = File(...)):
        tsv = self.ocr_service.image_to_tsv(file)
        return self.ocr_service.format_tsv_output(tsv)

    @router.post("/asset-to-tsv", response_model=list[OcrTsvResponse])
    def asset_to_tsv(self, req: OcrAssetReq):
        recipe_service = RecipeService(self.repos, self.user, self.group)
        recipe = recipe_service._get_recipe(req.recipe_slug)
        if recipe.id is None:
            return []
        data_service = RecipeDataService(recipe.id, recipe.group_id)
        asset_path = data_service.dir_assets.joinpath(req.asset_name)
        file = open(asset_path, "rb")
        tsv = self.ocr_service.image_to_tsv(file.read())

        return self.ocr_service.format_tsv_output(tsv)
