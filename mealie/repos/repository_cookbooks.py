import re
from collections.abc import Iterable

from fastapi import HTTPException, status
from pydantic import UUID4
from slugify import slugify
from sqlalchemy.exc import IntegrityError

from mealie.db.models.household.cookbook import CookBook
from mealie.repos.repository_generic import HouseholdRepositoryGeneric
from mealie.schema.cookbook.cookbook import ReadCookBook, SaveCookBook
from mealie.schema.response.responses import ErrorResponse


class RepositoryCookbooks(HouseholdRepositoryGeneric[ReadCookBook, CookBook]):
    def create(self, data: SaveCookBook | dict) -> ReadCookBook:
        if isinstance(data, dict):
            data = SaveCookBook(**data)
        data.slug = slugify(data.name)

        max_retries = 10
        for i in range(max_retries):
            try:
                return super().create(data)
            except IntegrityError:
                self.session.rollback()
                data.slug = slugify(f"{data.name} ({i + 1})")

        raise  # raise the last IntegrityError

    def create_many(self, data: Iterable[ReadCookBook | dict]) -> list[ReadCookBook]:
        return [self.create(entry) for entry in data]

    def update(self, match_value: str | int | UUID4, data: SaveCookBook | dict) -> ReadCookBook:
        new_data: dict = data if isinstance(data, dict) else data.model_dump()

        # UpdateCookBook (the bulk PUT /households/cookbooks route's schema) carries group_id/
        # household_id as plain client-settable fields - they exist so create_one() can stamp
        # them server-side, not so a caller can reassign an existing cookbook to another tenant.
        # The existence check upstream (HttpRepo.update_one) only confirms this cookbook is in
        # the caller's own scope, not that the submitted group_id/household_id still are. The
        # single-item update route's schema (CreateCookBook) has neither field at all, so these
        # are always added here rather than conditionally overwritten.
        if self.group_id is not None:
            new_data["group_id"] = self.group_id
        if self.household_id is not None:
            new_data["household_id"] = self.household_id

        data = SaveCookBook(**new_data)

        new_slug = slugify(data.name)
        if not (data.slug and re.match(rf"^({new_slug})(-\d+)?$", data.slug)):
            data.slug = new_slug

        max_retries = 10
        for i in range(max_retries):
            try:
                return super().update(match_value, data)
            except IntegrityError:
                self.session.rollback()
                data.slug = slugify(f"{data.name} ({i + 1})")

        raise  # raise the last IntegrityError

    def update_many(self, data: Iterable[ReadCookBook | dict]) -> list[ReadCookBook]:
        return [self.update(entry.id if isinstance(entry, ReadCookBook) else entry["id"], entry) for entry in data]

    def patch(self, match_value: str | int | UUID4, data: SaveCookBook | dict) -> ReadCookBook:
        cookbook = self.get_one(match_value)
        if not cookbook:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse.respond(message="Not found."),
            )
        cookbook_data = cookbook.model_dump()

        if not isinstance(data, dict):
            data = data.model_dump()
        return self.update(match_value, cookbook_data | data)
