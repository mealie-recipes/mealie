from fastapi import APIRouter, File

from mealie.routes._base import BaseUserController, controller
from mealie.schema.ocr.ocr import OcrTsvResponse
from mealie.services.ocr.pytesseract import OCR

router = APIRouter()


@controller(router)
class OCRController(BaseUserController):
    @router.post("/", response_model=str)
    def image_to_string(self, file: bytes = File(...)):
        return OCR.image_to_string(file)

    @router.post("/tsv", response_model=list[OcrTsvResponse])
    def image_to_tsv(self, file: bytes = File(...)):
        tsv = OCR.image_to_tsv(file)
        lines = tsv.split("\n")
        titles = [t.strip() for t in lines[0].split("\t")]
        response = []
        #  len-1 because the last line is empty
        for i in range(1, len(lines) - 1):
            d = {}
            for key, value in zip(titles, lines[i].split("\t")):
                if key == "text":
                    d[key] = value.strip()
                elif key == "conf":
                    d[key] = float(value.strip())
                else:
                    d[key] = int(value.strip())

            response.append(d)

        return response
