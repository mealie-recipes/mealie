import sqlalchemy.orm as orm
from mealie.db.models.group import Group
from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase
from requests import Session
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.orderinglist import ordering_list


class ShoppingListItem(SqlAlchemyBase, BaseMixins):
    __tablename__ = "shopping_list_items"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("shopping_lists.id"))
    position = Column(Integer, nullable=False)

    title = Column(String)
    text = Column(String)
    quantity = Column(Integer)
    checked = Column(Boolean)

    def __init__(self, title, text, quantity, checked, **_) -> None:
        self.title = title
        self.text = text
        self.quantity = quantity
        self.checked = checked


class ShoppingList(SqlAlchemyBase, BaseMixins):
    __tablename__ = "shopping_lists"
    id = Column(Integer, primary_key=True)

    group_id = Column(Integer, ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="shopping_lists")

    name = Column(String)
    items: list[ShoppingListItem] = orm.relationship(
        ShoppingListItem,
        cascade="all, delete, delete-orphan",
        order_by="ShoppingListItem.position",
        collection_class=ordering_list("position"),
    )

    def __init__(self, name, group, items, session=None, **_) -> None:
        self.name = name
        self.group = Group.get_ref(session, group)
        self.items = [ShoppingListItem(**i) for i in items]

    @staticmethod
    def get_ref(session: Session, id: int):
        return session.query(ShoppingList).filter(ShoppingList.id == id).one_or_none()
