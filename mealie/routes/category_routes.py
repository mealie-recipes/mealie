from typing import List

from models.category_models import Category
from services.category_services import get_all
from fastapi import APIRouter, HTTPException
from utils.snackbar import SnackResponse

router = APIRouter(tags=["Category"])

@router.get("/api/category/all", response_model=List[Category])
def get_all_categories():
    """ Returns a list of all categories """

    return get_all()