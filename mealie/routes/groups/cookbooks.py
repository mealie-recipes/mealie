from fastapi import Depends

from mealie.routes.routers import UserAPIRouter
from mealie.schema.cookbook.cookbook import CreateCookBook, ReadCookBook, RecipeCookBook
from mealie.services.cookbook import CookbookService

user_router = UserAPIRouter(prefix="/groups/cookbooks", tags=["Groups: Cookbooks"])


@user_router.get("", response_model=list[ReadCookBook])
def get_all_cookbook(cb_service: CookbookService = Depends(CookbookService.private)):
    """ Get cookbook from the Database """
    # Get Item
    return cb_service.get_all()


@user_router.post("", response_model=ReadCookBook)
def create_cookbook(data: CreateCookBook, cb_service: CookbookService = Depends(CookbookService.private)):
    """ Create cookbook in the Database """
    # Create Item
    return cb_service.create_one(data)


@user_router.put("", response_model=list[ReadCookBook])
def update_many(data: list[ReadCookBook], cb_service: CookbookService = Depends(CookbookService.private)):
    """ Create cookbook in the Database """
    # Create Item
    return cb_service.update_many(data)


@user_router.get("/{id}", response_model=RecipeCookBook)
def get_cookbook(cb_service: CookbookService = Depends(CookbookService.write_existing)):
    """ Get cookbook from the Database """
    # Get Item
    return cb_service.cookbook


@user_router.put("/{id}")
def update_cookbook(data: CreateCookBook, cb_service: CookbookService = Depends(CookbookService.write_existing)):
    """ Update cookbook in the Database """
    # Update Item
    return cb_service.update_one(data)


@user_router.delete("/{id}")
def delete_cookbook(cd_service: CookbookService = Depends(CookbookService.write_existing)):
    """ Delete cookbook from the Database """
    # Delete Item
    return cd_service.delete_one()
