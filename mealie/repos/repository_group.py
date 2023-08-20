from collections.abc import Iterable
from typing import cast
from uuid import UUID

from pydantic import UUID4
from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from mealie.db.models.group import Group
from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.tag import Tag
from mealie.db.models.recipe.tool import Tool
from mealie.db.models.users.users import User
from mealie.schema.group.group_statistics import GroupStatistics
from mealie.schema.user.user import GroupBase, GroupInDB

from ..db.models._model_base import SqlAlchemyBase
from .repository_generic import RepositoryGeneric


class RepositoryGroup(RepositoryGeneric[GroupInDB, Group]):
    def create(self, data: GroupBase | dict) -> GroupInDB:
        if isinstance(data, GroupBase):
            data = data.dict()

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

    def get_by_name(self, name: str) -> GroupInDB | None:
        dbgroup = self.session.execute(select(self.model).filter_by(name=name)).scalars().one_or_none()
        if dbgroup is None:
            return None
        return self.schema.from_orm(dbgroup)

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

    def statistics(self, group_id: UUID4) -> GroupStatistics:
        def model_count(model: type[SqlAlchemyBase]) -> int:
            stmt = select(func.count(model.id)).filter_by(group_id=group_id)
            return self.session.scalar(stmt)

        return GroupStatistics(
            total_recipes=model_count(RecipeModel),
            total_users=model_count(User),
            total_categories=model_count(Category),
            total_tags=model_count(Tag),
            total_tools=model_count(Tool),
        )
