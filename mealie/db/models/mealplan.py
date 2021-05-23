import sqlalchemy.orm as orm
from mealie.db.models.group import Group
from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.shopping_list import ShoppingList
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.ext.orderinglist import ordering_list


class Meal(SqlAlchemyBase):
    __tablename__ = "meal"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("mealdays.id"))
    position = Column(Integer)
    name = Column(String)
    slug = Column(String)
    description = Column(String)

    def __init__(self, slug, name="", description="", session=None) -> None:

        if slug and slug != "":
            recipe: RecipeModel = session.query(RecipeModel).filter(RecipeModel.slug == slug).one_or_none()

            if recipe:
                name = recipe.name
                self.slug = recipe.slug
                description = recipe.description

        self.name = name
        self.description = description


class MealDay(SqlAlchemyBase, BaseMixins):
    __tablename__ = "mealdays"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("mealplan.uid"))
    date = Column(Date)
    meals: list[Meal] = orm.relationship(
        Meal,
        cascade="all, delete, delete-orphan",
        order_by="Meal.position",
        collection_class=ordering_list("position"),
    )

    def __init__(self, date, meals: list, session=None):
        self.date = date
        self.meals = [Meal(**m, session=session) for m in meals]


class MealPlan(SqlAlchemyBase, BaseMixins):
    __tablename__ = "mealplan"
    uid = Column(Integer, primary_key=True, unique=True)
    start_date = Column(Date)
    end_date = Column(Date)
    plan_days: list[MealDay] = orm.relationship(MealDay, cascade="all, delete, delete-orphan")

    group_id = Column(Integer, ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="mealplans")

    shopping_list_id = Column(Integer, ForeignKey("shopping_lists.id"))
    shopping_list: ShoppingList = orm.relationship("ShoppingList", single_parent=True)

    def __init__(
        self,
        start_date,
        end_date,
        plan_days,
        group: str,
        shopping_list: int = None,
        session=None,
        **_,
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.group = Group.get_ref(session, group)

        if shopping_list:
            self.shopping_list = ShoppingList.get_ref(session, shopping_list)

        self.plan_days = [MealDay(**day, session=session) for day in plan_days]
