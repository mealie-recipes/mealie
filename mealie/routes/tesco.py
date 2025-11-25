from fastapi import APIRouter, Depends
from mealie.schema.tesco import TescoProduct
from mealie.services.tesco.tesco_service import TescoService

router = APIRouter(prefix="/api/tesco", tags=["Tesco"])

@router.get("/price", response_model=TescoProduct)
async def get_tesco_price(url: str):
    service = TescoService()
    return await service.get_product_price(url)
