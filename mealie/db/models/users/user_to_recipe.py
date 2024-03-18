from sqlalchemy import Boolean, Column, Float, ForeignKey, UniqueConstraint, event, func
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.session import Session

from .._model_base import SqlAlchemyBase
from .._model_utils import GUID


class UserToRecipe(SqlAlchemyBase):
    __tablename__ = "users_to_recipes"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="user_id_recipe_id_key"),)

    user_id = Column(GUID, ForeignKey("users.id"), index=True, primary_key=True)
    recipe_id = Column(GUID, ForeignKey("recipes.id"), index=True, primary_key=True)
    rating = Column(Float, index=True, nullable=True)
    is_favorite = Column(Boolean, index=True, nullable=False)


@event.listens_for(UserToRecipe, "after_insert")
@event.listens_for(UserToRecipe, "after_delete")
@event.listens_for(UserToRecipe.rating, "set")
def update_recipe_rating(connection: Connection, target: UserToRecipe):
    from mealie.db.models.recipe.recipe import RecipeModel

    with Session(bind=connection) as session:
        recipe_id = target.recipe_id
        recipe = session.query(RecipeModel).filter(RecipeModel.id == target.recipe_id).first()
        if not recipe:
            return

        recipe.rating = (
            session.query(func.avg(UserToRecipe.rating)).filter(UserToRecipe.recipe_id == recipe_id).scalar()
        )
        session.commit()
