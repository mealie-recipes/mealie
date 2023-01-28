from pydantic import UUID4
from sqlalchemy import func, select

from mealie.db.models.group import Group
from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.tag import Tag
from mealie.db.models.recipe.tool import Tool
from mealie.db.models.users.users import User
from mealie.schema.group.group_statistics import GroupStatistics
from mealie.schema.user.user import GroupInDB

from ..db.models._model_base import SqlAlchemyBase
from .repository_generic import RepositoryGeneric


class RepositoryGroup(RepositoryGeneric[GroupInDB, Group]):
    def get_by_name(self, name: str) -> GroupInDB | None:
        dbgroup = self.session.execute(select(self.model).filter_by(name=name)).scalars().one_or_none()
        if dbgroup is None:
            return None
        return self.schema.from_orm(dbgroup)

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
