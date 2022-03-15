from typing import Optional, Union

from sqlalchemy.orm.session import Session

from mealie.db.models.group import Group
from mealie.schema.meal_plan.meal import MealPlanOut
from mealie.schema.user.user import GroupInDB

from .repository_generic import RepositoryGeneric


class RepositoryGroup(RepositoryGeneric[GroupInDB, Group]):
    def get_meals(self, session: Session, match_value: str, match_key: str = "name") -> list[MealPlanOut]:
        """A Helper function to get the group from the database and return a sorted list of

        Args:
            session (Session): SqlAlchemy Session
            match_value (str): Match Value
            match_key (str, optional): Match Key. Defaults to "name".

        Returns:
            list[MealPlanOut]: [description]
        """
        group: GroupInDB = session.query(self.sql_model).filter_by(**{match_key: match_value}).one_or_none()

        return group.mealplans

    def get_by_name(self, name: str, limit=1) -> Union[GroupInDB, Group, None]:
        dbgroup = self.session.query(self.sql_model).filter_by(**{"name": name}).one_or_none()
        if dbgroup is None:
            return None
        return self.schema.from_orm(dbgroup)
