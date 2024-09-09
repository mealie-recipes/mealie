from collections.abc import Iterable

from slugify import slugify
from sqlalchemy.exc import IntegrityError

from mealie.db.models.household.cookbook import CookBook
from mealie.repos.repository_generic import HouseholdRepositoryGeneric
from mealie.schema.cookbook.cookbook import ReadCookBook, SaveCookBook


class RepositoryCookbooks(HouseholdRepositoryGeneric[ReadCookBook, CookBook]):
    def create(self, data: SaveCookBook | dict) -> ReadCookBook:
        if isinstance(data, dict):
            data = SaveCookBook(**data)
        data.slug = slugify(data.name)

        max_retries = 10
        original_name = data.name
        for i in range(max_retries):
            try:
                return super().create(data)
            except IntegrityError:
                self.session.rollback()
                data.slug = slugify(f"{original_name} ({i+1})")

        raise  # raise the last IntegrityError

    def create_many(self, data: Iterable[ReadCookBook | dict]) -> list[ReadCookBook]:
        return [self.create(entry) for entry in data]
