from fastapi import APIRouter, Depends
from mealie.core.root_logger import get_logger
from mealie.routes.deps import get_current_user

router = APIRouter(prefix="/api/units", dependencies=[Depends(get_current_user)])
logger = get_logger()


@router.post("")
async def create_food():
    """ Create food in the Database """
    # Create food
    pass


@router.get("/{id}")
async def get_food():
    """ Get food from the Database """
    # Get food
    pass


@router.put("/{id}")
async def update_food():
    """ Update food in the Database """
    # Update food
    pass


@router.delete("/{id}")
async def delete_food():
    """ Delete food from the Database """
    # Delete food
    pass
