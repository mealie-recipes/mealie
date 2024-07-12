from collections.abc import Iterable
from typing import cast
from uuid import UUID

from pydantic import UUID4
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from mealie.db.models.household.household import Household
from mealie.repos.repository_generic import GroupRepositoryGeneric
from mealie.schema.household.household import HouseholdBase, HouseholdOut, UpdateHousehold


class RepositoryHousehold(GroupRepositoryGeneric[HouseholdOut, Household]):
    def create(self, data: HouseholdBase | dict) -> HouseholdOut:
        if isinstance(data, HouseholdBase):
            data = data.model_dump()

        max_attempts = 10
        original_name = cast(str, data["name"])

        attempts = 0
        while True:
            try:
                data["slug"] = slugify(data["name"])
                return super().create(data)
            except IntegrityError:
                self.session.rollback()
                attempts += 1
                if attempts >= max_attempts:
                    raise

                data["name"] = f"{original_name} ({attempts})"

    def create_many(self, data: Iterable[HouseholdOut | dict]) -> list[HouseholdOut]:
        # since create uses special logic for resolving slugs, we don't want to use the standard create_many method
        return [self.create(new_household) for new_household in data]

    def update(self, match_value: str | int | UUID4, new_data: UpdateHousehold | dict) -> HouseholdOut:
        if isinstance(new_data, HouseholdBase):
            new_data.slug = slugify(new_data.name)
        else:
            new_data["slug"] = slugify(new_data["name"])

        return super().update(match_value, new_data)

    def update_many(self, data: Iterable[UpdateHousehold | dict]) -> list[HouseholdOut]:
        # since update uses special logic for resolving slugs, we don't want to use the standard update_many method
        return [
            self.update(household["id"] if isinstance(household, dict) else household.id, household)
            for household in data
        ]

    def get_by_name(self, name: str) -> HouseholdOut | None:
        dbhousehold = self.session.execute(select(self.model).filter_by(name=name)).scalars().one_or_none()
        if dbhousehold is None:
            return None
        return self.schema.model_validate(dbhousehold)

    def get_by_slug_or_id(self, slug_or_id: str | UUID) -> HouseholdOut | None:
        if isinstance(slug_or_id, str):
            try:
                slug_or_id = UUID(slug_or_id)
            except ValueError:
                pass

        if isinstance(slug_or_id, UUID):
            return self.get_one(slug_or_id)
        else:
            return self.get_one(slug_or_id, key="slug")
