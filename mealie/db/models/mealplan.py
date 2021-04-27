from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as orm
from mealie.db.models.group import Group
from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase


class Meal(SqlAlchemyBase):
    __tablename__ = "meal"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("mealplan.uid"))
    slug = sa.Column(sa.String)
    name = sa.Column(sa.String)
    date = sa.Column(sa.Date)
    image = sa.Column(sa.String)
    description = sa.Column(sa.String)

    def __init__(self, slug, name, date, image, description, session=None) -> None:
        self.slug = slug
        self.name = name
        self.date = date
        self.image = image
        self.description = description


class MealPlanModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "mealplan"
    uid = sa.Column(sa.Integer, primary_key=True, unique=True)  # ! Probably Bad?
    startDate = sa.Column(sa.Date)
    endDate = sa.Column(sa.Date)
    meals: List[Meal] = orm.relationship(Meal, cascade="all, delete, delete-orphan")
    group_id = sa.Column(sa.Integer, sa.ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="mealplans")

    def __init__(self, startDate, endDate, meals, group: str, uid=None, session=None) -> None:
        self.startDate = startDate
        self.endDate = endDate
        self.group = Group.get_ref(session, group)
        self.meals = [Meal(**meal) for meal in meals]

    def update(self, session, startDate, endDate, meals, uid, group) -> None:

        self.__init__(
            startDate=startDate,
            endDate=endDate,
            meals=meals,
            group=group,
            session=session,
        )
