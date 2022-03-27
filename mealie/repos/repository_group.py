from typing import Union

from pydantic import UUID4

from mealie.db.models.group import Group
from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.tag import Tag
from mealie.db.models.recipe.tool import Tool
from mealie.db.models.users.users import User
from mealie.schema.group.group_statistics import GroupStatistics
from mealie.schema.user.user import GroupInDB

from .repository_generic import RepositoryGeneric


class RepositoryGroup(RepositoryGeneric[GroupInDB, Group]):
    def get_by_name(self, name: str, limit=1) -> Union[GroupInDB, Group, None]:
        dbgroup = self.session.query(self.sql_model).filter_by(**{"name": name}).one_or_none()
        if dbgroup is None:
            return None
        return self.schema.from_orm(dbgroup)

    def statistics(self, group_id: UUID4) -> GroupStatistics:
        return GroupStatistics(
            total_recipes=self.session.query(RecipeModel).filter_by(group_id=group_id).count(),
            total_users=self.session.query(User).filter_by(group_id=group_id).count(),
            total_categories=self.session.query(Category).filter_by(group_id=group_id).count(),
            total_tags=self.session.query(Tag).filter_by(group_id=group_id).count(),
            total_tools=self.session.query(Tool).filter_by(group_id=group_id).count(),
        )
