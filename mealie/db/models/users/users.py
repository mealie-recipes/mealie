from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, orm

from mealie.core.config import settings
from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models.group import Group
from mealie.db.models.recipe.recipe import RecipeModel


class LongLiveToken(SqlAlchemyBase, BaseMixins):
    __tablename__ = "long_live_tokens"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    token = Column(String, nullable=False)
    user = orm.relationship("User")

    def __init__(self, session, name, token, parent_id) -> None:
        self.name = name
        self.token = token
        self.user = User.get_ref(session, parent_id)


class User(SqlAlchemyBase, BaseMixins):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, index=True)
    username = Column(String, index=True, unique=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    admin = Column(Boolean, default=False)
    advanced = Column(Boolean, default=False)

    group_id = Column(Integer, ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="users")

    tokens: list[LongLiveToken] = orm.relationship(
        LongLiveToken, back_populates="user", cascade="all, delete, delete-orphan", single_parent=True
    )

    comments: list = orm.relationship(
        "RecipeComment", back_populates="user", cascade="all, delete, delete-orphan", single_parent=True
    )

    favorite_recipes: list[RecipeModel] = orm.relationship(RecipeModel, back_populates="favorited_by")

    def __init__(
        self,
        session,
        full_name,
        email,
        password,
        favorite_recipes: list[str] = None,
        group: str = settings.DEFAULT_GROUP,
        admin=False,
        advanced=False,
        **_
    ) -> None:

        group = group or settings.DEFAULT_GROUP
        favorite_recipes = favorite_recipes or []
        self.full_name = full_name
        self.email = email
        self.group = Group.get_ref(session, group)
        self.admin = admin
        self.password = password
        self.advanced = advanced

        self.favorite_recipes = [
            RecipeModel.get_ref(session=session, match_value=x, match_attr="slug") for x in favorite_recipes
        ]

        if self.username is None:
            self.username = full_name

    def update(
        self,
        full_name,
        email,
        group,
        admin,
        username,
        session=None,
        favorite_recipes=None,
        password=None,
        advanced=False,
        **_
    ):
        favorite_recipes = favorite_recipes or []
        self.username = username
        self.full_name = full_name
        self.email = email
        self.group = Group.get_ref(session, group)
        self.admin = admin
        self.advanced = advanced

        if self.username is None:
            self.username = full_name

        if password:
            self.password = password

        self.favorite_recipes = [
            RecipeModel.get_ref(session=session, match_value=x, match_attr="slug") for x in favorite_recipes
        ]

    def update_password(self, password):
        self.password = password

    @staticmethod
    def get_ref(session, id: str):
        return session.query(User).filter(User.id == id).one()
