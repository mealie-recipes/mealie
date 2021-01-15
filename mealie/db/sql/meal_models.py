import uuid
from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.sql.model_base import SqlAlchemyBase


class Meal(SqlAlchemyBase):
    __tablename__ = "meal"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("mealplan.uid"))
    slug = sa.Column(sa.String)
    name = sa.Column(sa.String)
    date = sa.Column(sa.Date)
    dateText = sa.Column(sa.String)
    image = sa.Column(sa.String)
    description = sa.Column(sa.String)

    def dict(self) -> dict:
        data = {
            "slug": self.slug,
            "name": self.name,
            "date": self.date,
            "dateText": self.dateText,
            "image": self.image,
            "description": self.description,
        }

        return data


class MealPlanModel(SqlAlchemyBase):
    __tablename__ = "mealplan"
    uid = sa.Column(
        sa.String, default=uuid.uuid1, primary_key=True, unique=True
    )  #! Probably Bad?
    startDate = sa.Column(sa.Date)
    endDate = sa.Column(sa.Date)
    meals: List[Meal] = orm.relation(Meal)

    def __init__(self, startDate, endDate, meals) -> None:
        self.startDate = startDate
        self.endDate = endDate
        self.meals = [Meal(meal) for meal in meals]

    def update(self, startDate, endDate, meals) -> None:
        self.__init__(startDate, endDate, meals)

    def dict(self) -> dict:
        data = {
            "uid": self.uid,
            "startDate": self.startDate,
            "endDate": self.endDate,
            "meals": [meal.dict() for meal in self.meals],
        }

        return data
