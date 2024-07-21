from collections.abc import Iterable
from typing import cast
from uuid import UUID

from pydantic import UUID4
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from mealie.db.models.group import Group
from mealie.schema.user.user import GroupBase, GroupInDB, UpdateGroup

from .repository_generic import RepositoryGeneric


class RepositoryGroup(RepositoryGeneric[GroupInDB, Group]):
    def create(self, data: GroupBase | dict) -> GroupInDB:
        if isinstance(data, GroupBase):
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

    def create_many(self, data: Iterable[GroupInDB | dict]) -> list[GroupInDB]:
        # since create uses special logic for resolving slugs, we don't want to use the standard create_many method
        return [self.create(new_group) for new_group in data]

    def update(self, match_value: str | int | UUID4, new_data: UpdateGroup | dict) -> GroupInDB:
        if isinstance(new_data, GroupBase):
            new_data.slug = slugify(new_data.name)
        else:
            new_data["slug"] = slugify(new_data["name"])

        return super().update(match_value, new_data)

    def update_many(self, data: Iterable[UpdateGroup | dict]) -> list[GroupInDB]:
        # since update uses special logic for resolving slugs, we don't want to use the standard update_many method
        return [self.update(group["id"] if isinstance(group, dict) else group.id, group) for group in data]

    def get_by_name(self, name: str) -> GroupInDB | None:
        dbgroup = self.session.execute(select(self.model).filter_by(name=name)).scalars().one_or_none()
        if dbgroup is None:
            return None
        return self.schema.model_validate(dbgroup)

    def get_by_slug_or_id(self, slug_or_id: str | UUID) -> GroupInDB | None:
        if isinstance(slug_or_id, str):
            try:
                slug_or_id = UUID(slug_or_id)
            except ValueError:
                pass

        if isinstance(slug_or_id, UUID):
            return self.get_one(slug_or_id)
        else:
            return self.get_one(slug_or_id, key="slug")
