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
        if isinstance(data, dict):
            data = SaveCookBook(**data)

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
