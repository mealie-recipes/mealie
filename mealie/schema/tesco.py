from typing import Optional
from pydantic import BaseModel

class TescoProduct(BaseModel):
    url: str
    name: Optional[str] = None
    price: Optional[float] = None
    price_per_unit: Optional[float] = None
    units: Optional[str] = None
    quantity: Optional[float] = None
    price_valid_until: Optional[str] = None
    status_code: Optional[int] = None
    scrape_success: bool = False
