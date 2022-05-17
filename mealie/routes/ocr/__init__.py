from fastapi import APIRouter

from . import pytesseract

router = APIRouter(prefix="/ocr")

router.include_router(pytesseract.router)
