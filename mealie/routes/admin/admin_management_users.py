from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.core import security
from mealie.routes._base import BaseAdminController, controller
from mealie.routes._base.dependencies import SharedDependencies
from mealie.routes._base.mixins import CrudMixins
from mealie.schema.query import GetAll
from mealie.schema.response.responses import ErrorResponse
from mealie.schema.user.user import UserIn, UserOut

router = APIRouter(prefix="/users", tags=["Admin: Users"])


@controller(router)
class AdminUserManagementRoutes(BaseAdminController):
    deps: SharedDependencies = Depends(SharedDependencies.user)

    @cached_property
    def repo(self):
        if not self.deps.acting_user:
            raise Exception("No user is logged in.")

        return self.deps.repos.users

    # =======================================================================
    # CRUD Operations

    @property
    def mixins(self):
        return CrudMixins[UserIn, UserOut, UserOut](self.repo, self.deps.logger, self.registered_exceptions)

    @router.get("", response_model=list[UserOut])
    def get_all(self, q: GetAll = Depends(GetAll)):
        return self.repo.get_all(start=q.start, limit=q.limit, override_schema=UserOut)

    @router.post("", response_model=UserOut, status_code=201)
    def create_one(self, data: UserIn):
        data.password = security.hash_password(data.password)
        return self.mixins.create_one(data)

    @router.get("/{item_id}", response_model=UserOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=UserOut)
    def update_one(self, item_id: UUID4, data: UserOut):
        # Prevent self demotion
        if self.deps.acting_user.id == item_id and self.deps.acting_user.admin != data.admin:
            raise HTTPException(status_code=403, detail=ErrorResponse.respond("you cannot demote yourself"))

        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=UserOut)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)
