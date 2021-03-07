import sqlalchemy as sa
import sqlalchemy.orm as orm
from core.config import DEFAULT_GROUP
from db.models.model_base import BaseMixins, SqlAlchemyBase
from fastapi.logger import logger
from slugify import slugify


class Group(SqlAlchemyBase, BaseMixins):
    __tablename__ = "groups"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, index=True, nullable=False, unique=True)
    users = orm.relationship("User", back_populates="group")
    mealplans = orm.relationship("MealPlanModel", back_populates="group")

    def __init__(self, name, session=None) -> None:
        self.name = name

    @staticmethod
    def create_if_not_exist(session, name: str = DEFAULT_GROUP):
        try:
            result = session.query(Group).filter(Group.name == name).one()
            if result:
                logger.info("Category exists, associating recipe")
                return result
            else:
                logger.info("Category doesn't exists, creating tag")
                return Group(name=name)
        except:
            logger.info("Category doesn't exists, creating category")
            return Group(name=name)
