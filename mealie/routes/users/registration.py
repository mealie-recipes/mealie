from fastapi import APIRouter, status

from mealie.repos.all_repositories import get_repositories
from mealie.routes._base import BasePublicController, controller
from mealie.schema.user.registration import CreateUserRegistration
from mealie.schema.user.user import UserOut
from mealie.services.user_services.registration_service import RegistrationService

router = APIRouter(prefix="/register")


@controller(router)
class RegistrationController(BasePublicController):
    @router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
    def register_new_user(self, data: CreateUserRegistration):
        registration_service = RegistrationService(self.deps.logger, get_repositories(self.deps.session))
        return registration_service.register_user(data)
