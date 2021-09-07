from fastapi import APIRouter, Depends, status

from mealie.schema.user.registration import CreateUserRegistration
from mealie.schema.user.user import UserOut
from mealie.services.user_services.registration_service import RegistrationService

router = APIRouter(prefix="/register")


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_new_user(
    data: CreateUserRegistration, registration_service: RegistrationService = Depends(RegistrationService.public)
):
    return registration_service.register_user(data)
