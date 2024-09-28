from logging import Logger
from uuid import uuid4

from fastapi import HTTPException, status
from pydantic import UUID4

from mealie.core.config import get_app_settings
from mealie.core.security import hash_password
from mealie.lang.providers import Translator
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.group_preferences import CreateGroupPreferences
from mealie.schema.household.household import HouseholdCreate, HouseholdInDB
from mealie.schema.household.household_preferences import CreateHouseholdPreferences
from mealie.schema.user.registration import CreateUserRegistration
from mealie.schema.user.user import GroupBase, GroupInDB, PrivateUser, UserIn
from mealie.services.group_services.group_service import GroupService
from mealie.services.household_services.household_service import HouseholdService
from mealie.services.seeder.seeder_service import SeederService


class RegistrationService:
    logger: Logger
    repos: AllRepositories

    def __init__(self, logger: Logger, db: AllRepositories, translator: Translator):
        self.logger = logger
        self.repos = db
        self.t = translator.t

    def _create_new_user(self, group: GroupInDB, household: HouseholdInDB, new_group: bool) -> PrivateUser:
        new_user = UserIn(
            email=self.registration.email,
            username=self.registration.username,
            password=hash_password(self.registration.password),
            full_name=self.registration.full_name,
            advanced=self.registration.advanced,
            group=group,
            household=household,
            can_invite=new_group,
            can_manage=new_group,
            can_manage_household=new_group,
            can_organize=new_group,
        )

        # TODO: problem with repository type, not type here
        return self.repos.users.create(new_user)  # type: ignore

    def _register_new_group(self) -> GroupInDB:
        group_data = GroupBase(name=self.registration.group)

        group_preferences = CreateGroupPreferences(
            group_id=uuid4(),
            private_group=self.registration.private,
        )

        return GroupService.create_group(self.repos, group_data, group_preferences)

    def _fetch_or_register_new_household(self, group_id: UUID4) -> HouseholdInDB:
        settings = get_app_settings()
        new_household_name = self.registration.household or settings.DEFAULT_HOUSEHOLD

        group_repos = get_repositories(self.repos.session, group_id=group_id)
        household_fetch = group_repos.households.get_by_name(new_household_name)
        if household_fetch:
            return household_fetch

        household_data = HouseholdCreate(name=new_household_name)
        household_preferences = CreateHouseholdPreferences(
            private_household=self.registration.private,
            first_day_of_week=0,
            recipe_public=not self.registration.private,
            recipe_show_nutrition=self.registration.advanced,
            recipe_show_assets=self.registration.advanced,
            recipe_landscape_view=False,
            recipe_disable_comments=self.registration.advanced,
            recipe_disable_amount=self.registration.advanced,
        )
        return HouseholdService.create_household(group_repos, household_data, household_preferences)

    def register_user(self, registration: CreateUserRegistration) -> PrivateUser:
        self.registration = registration

        if self.repos.users.get_by_username(registration.username):
            raise HTTPException(status.HTTP_409_CONFLICT, {"message": self.t("exceptions.username-conflict-error")})
        elif self.repos.users.get_one(registration.email, "email"):
            raise HTTPException(status.HTTP_409_CONFLICT, {"message": self.t("exceptions.email-conflict-error")})

        token_entry = None
        new_group = False

        if registration.group_token:
            token_entry = self.repos.group_invite_tokens.get_one(registration.group_token)
            if not token_entry:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, {"message": "Invalid group token"})

            maybe_none_group = self.repos.groups.get_one(token_entry.group_id)
            if maybe_none_group is None:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, {"message": "Invalid group token"})
            group = maybe_none_group

            maybe_none_household = self.repos.households.get_one(token_entry.household_id)
            if maybe_none_household is None:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, {"message": "Invalid group token"})
            household = maybe_none_household
        elif registration.group:
            new_group = True
            group = self._register_new_group()
            household = self._fetch_or_register_new_household(group.id)
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"message": "Missing group"})

        self.logger.info(f"Registering user {registration.username}")
        user = self._create_new_user(group, household, new_group)

        if new_group and registration.seed_data:
            seeder_service = SeederService(self.repos)
            seeder_service.seed_foods(registration.locale)
            seeder_service.seed_labels(registration.locale)
            seeder_service.seed_units(registration.locale)

        if token_entry and user:
            token_entry.uses_left = token_entry.uses_left - 1

            if token_entry.uses_left == 0:
                self.repos.group_invite_tokens.delete(token_entry.token)

            else:
                self.repos.group_invite_tokens.update(token_entry.token, token_entry)

        return user
