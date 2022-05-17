from fastapi import APIRouter, File

from mealie.routes._base import BaseUserController, controller
from mealie.services.ocr.pytesseract import OCR

router = APIRouter()


@controller(router)
class OCRController(BaseUserController):
    @router.post("/", response_model=str)
    def image_to_string(self, file: bytes = File(...)):
        return OCR.image_to_string(file)
