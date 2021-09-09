from fastapi import HTTPException, status

from mealie.core.root_logger import get_logger
from mealie.core.security import hash_password
from mealie.schema.group.group_preferences import CreateGroupPreferences
from mealie.schema.user.registration import CreateUserRegistration
from mealie.schema.user.user import GroupBase, GroupInDB, PrivateUser, UserIn
from mealie.services._base_http_service.http_services import PublicHttpService
from mealie.services.events import create_user_event
from mealie.services.group_services.group_mixins import create_new_group

logger = get_logger(module=__name__)


class RegistrationService(PublicHttpService[int, str]):
    event_func = create_user_event

    def populate_item() -> None:
        pass

    def register_user(self, registration: CreateUserRegistration) -> PrivateUser:
        self.registration = registration

        logger.info(f"Registering user {registration.username}")
        token_entry = None

        if g_token := registration.group_token:
            token_entry = self.db.group_tokens.get(self.session, g_token)

            if not token_entry:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, {"message": "Invalid group token"})

            group = self.db.groups.get(self.session, token_entry.group_id)

        elif registration.group:
            group = self._register_new_group()

        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"message": "Missing group"})

        user = self._create_new_user(group)

        if token_entry:
            token_entry.uses_left = token_entry.uses_left - 1

            if token_entry.uses_left == 0:
                self.db.group_tokens.delete(self.session, token_entry.token)

            else:
                self.db.group_tokens.update(self.session, token_entry.token, token_entry)

        return user

    def _create_new_user(self, group: GroupInDB) -> PrivateUser:
        new_user = UserIn(
            email=self.registration.email,
            username=self.registration.username,
            password=hash_password(self.registration.password),
            full_name=self.registration.username,
            advanced=self.registration.advanced,
            group=group.name,
        )

        return self.db.users.create(self.session, new_user)

    def _register_new_group(self) -> GroupInDB:
        group_data = GroupBase(name=self.registration.group)

        group_preferences = CreateGroupPreferences(
            group_id=0,
            private_group=self.registration.private,
            first_day_of_week=0,
            recipe_public=not self.registration.private,
            recipe_show_nutrition=self.registration.advanced,
            recipe_show_assets=self.registration.advanced,
            recipe_landscape_view=False,
            recipe_disable_comments=self.registration.advanced,
            recipe_disable_amount=self.registration.advanced,
        )

        return create_new_group(self.session, group_data, group_preferences)
