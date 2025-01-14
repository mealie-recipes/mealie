from typing import TYPE_CHECKING

import sqlalchemy as sa
from pydantic import ConfigDict
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, event, orm
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.session import Session

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models.labels import MultiPurposeLabel
from mealie.db.models.recipe.api_extras import IngredientFoodExtras, api_extras

from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..group import Group
    from ..household import Household


households_to_ingredient_foods = sa.Table(
    "households_to_ingredient_foods",
    SqlAlchemyBase.metadata,
    sa.Column("household_id", GUID, sa.ForeignKey("households.id"), index=True),
    sa.Column("food_id", GUID, sa.ForeignKey("ingredient_foods.id"), index=True),
    sa.UniqueConstraint("household_id", "food_id", name="household_id_food_id_key"),
)


class IngredientUnitModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ingredient_units"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    # ID Relationships
    group_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="ingredient_units", foreign_keys=[group_id])

    name: Mapped[str | None] = mapped_column(String)
    plural_name: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)
    abbreviation: Mapped[str | None] = mapped_column(String)
    plural_abbreviation: Mapped[str | None] = mapped_column(String)
    use_abbreviation: Mapped[bool | None] = mapped_column(Boolean, default=False)
    fraction: Mapped[bool | None] = mapped_column(Boolean, default=True)

    ingredients: Mapped[list["RecipeIngredientModel"]] = orm.relationship(
        "RecipeIngredientModel", back_populates="unit"
    )
    aliases: Mapped[list["IngredientUnitAliasModel"]] = orm.relationship(
        "IngredientUnitAliasModel",
        back_populates="unit",
        cascade="all, delete, delete-orphan",
    )

    # Automatically updated by sqlalchemy event, do not write to this manually
    name_normalized: Mapped[str | None] = mapped_column(sa.String, index=True)
    plural_name_normalized: Mapped[str | None] = mapped_column(sa.String, index=True)
    abbreviation_normalized: Mapped[str | None] = mapped_column(String, index=True)
    plural_abbreviation_normalized: Mapped[str | None] = mapped_column(String, index=True)

    @auto_init()
    def __init__(
        self,
        session: Session,
        name: str | None = None,
        plural_name: str | None = None,
        abbreviation: str | None = None,
        plural_abbreviation: str | None = None,
        **_,
    ) -> None:
        if name is not None:
            self.name_normalized = self.normalize(name)
        if plural_name is not None:
            self.plural_name_normalized = self.normalize(plural_name)
        if abbreviation is not None:
            self.abbreviation_normalized = self.normalize(abbreviation)
        if plural_abbreviation is not None:
            self.plural_abbreviation_normalized = self.normalize(plural_abbreviation)

        tableargs = [
            sa.UniqueConstraint("name", "group_id", name="ingredient_units_name_group_id_key"),
            sa.Index(
                "ix_ingredient_units_name_normalized",
                "name_normalized",
                unique=False,
            ),
            sa.Index(
                "ix_ingredient_units_plural_name_normalized",
                "plural_name_normalized",
                unique=False,
            ),
            sa.Index(
                "ix_ingredient_units_abbreviation_normalized",
                "abbreviation_normalized",
                unique=False,
            ),
            sa.Index(
                "ix_ingredient_units_plural_abbreviation_normalized",
                "plural_abbreviation_normalized",
                unique=False,
            ),
        ]

        if session.get_bind().name == "postgresql":
            tableargs.extend(
                [
                    sa.Index(
                        "ix_ingredient_units_name_normalized_gin",
                        "name_normalized",
                        unique=False,
                        postgresql_using="gin",
                        postgresql_ops={
                            "name_normalized": "gin_trgm_ops",
                        },
                    ),
                    sa.Index(
                        "ix_ingredient_units_plural_name_normalized_gin",
                        "name_normalized",
                        unique=False,
                        postgresql_using="gin",
                        postgresql_ops={
                            "plural_name_normalized": "gin_trgm_ops",
                        },
                    ),
                    sa.Index(
                        "ix_ingredient_units_abbreviation_normalized_gin",
                        "abbreviation_normalized",
                        unique=False,
                        postgresql_using="gin",
                        postgresql_ops={
                            "abbreviation_normalized": "gin_trgm_ops",
                        },
                    ),
                    sa.Index(
                        "ix_ingredient_units_plural_abbreviation_normalized_gin",
                        "plural_abbreviation_normalized",
                        unique=False,
                        postgresql_using="gin",
                        postgresql_ops={
                            "plural_abbreviation_normalized": "gin_trgm_ops",
                        },
                    ),
                ]
            )

        self.__table_args__ = tuple(tableargs)


class IngredientFoodModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ingredient_foods"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    # ID Relationships
    group_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="ingredient_foods", foreign_keys=[group_id])
    households_with_ingredient_food: Mapped[list["Household"]] = orm.relationship(
        "Household", secondary=households_to_ingredient_foods, back_populates="ingredient_foods_on_hand"
    )

    name: Mapped[str | None] = mapped_column(String)
    plural_name: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)

    ingredients: Mapped[list["RecipeIngredientModel"]] = orm.relationship(
        "RecipeIngredientModel", back_populates="food"
    )
    aliases: Mapped[list["IngredientFoodAliasModel"]] = orm.relationship(
        "IngredientFoodAliasModel",
        back_populates="food",
        cascade="all, delete, delete-orphan",
    )
    extras: Mapped[list[IngredientFoodExtras]] = orm.relationship("IngredientFoodExtras", cascade="all, delete-orphan")

    label_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("multi_purpose_labels.id"), index=True)
    label: Mapped[MultiPurposeLabel | None] = orm.relationship(MultiPurposeLabel, uselist=False, back_populates="foods")

    # Automatically updated by sqlalchemy event, do not write to this manually
    name_normalized: Mapped[str | None] = mapped_column(sa.String, index=True)
    plural_name_normalized: Mapped[str | None] = mapped_column(sa.String, index=True)

    model_config = ConfigDict(
        exclude={
            "households_with_ingredient_food",
        }
    )

    # Deprecated
    on_hand: Mapped[bool] = mapped_column(Boolean, default=False)

    @api_extras
    @auto_init()
    def __init__(
        self,
        session: Session,
        group_id: GUID,
        name: str | None = None,
        plural_name: str | None = None,
        households_with_ingredient_food: list[str] | None = None,
        **_,
    ) -> None:
        from ..household import Household

        if name is not None:
            self.name_normalized = self.normalize(name)
        if plural_name is not None:
            self.plural_name_normalized = self.normalize(plural_name)

        if not households_with_ingredient_food:
            self.households_with_ingredient_food = []
        else:
            self.households_with_ingredient_food = (
                session.query(Household)
                .filter(Household.group_id == group_id, Household.slug.in_(households_with_ingredient_food))
                .all()
            )

        tableargs = [
            sa.UniqueConstraint("name", "group_id", name="ingredient_foods_name_group_id_key"),
            sa.Index(
                "ix_ingredient_foods_name_normalized",
                "name_normalized",
                unique=False,
            ),
            sa.Index(
                "ix_ingredient_foods_plural_name_normalized",
                "plural_name_normalized",
                unique=False,
            ),
        ]

        if session.get_bind().name == "postgresql":
            tableargs.extend(
                [
                    sa.Index(
                        "ix_ingredient_foods_name_normalized_gin",
                        "name_normalized",
                        unique=False,
                        postgresql_using="gin",
                        postgresql_ops={
                            "name_normalized": "gin_trgm_ops",
                        },
                    ),
                    sa.Index(
                        "ix_ingredient_foods_plural_name_normalized_gin",
                        "plural_name_normalized",
                        unique=False,
                        postgresql_using="gin",
                        postgresql_ops={
                            "plural_name_normalized": "gin_trgm_ops",
                        },
                    ),
                ]
            )

        self.__table_args__ = tuple(tableargs)


class IngredientUnitAliasModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ingredient_units_aliases"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    unit_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("ingredient_units.id"), primary_key=True)
    unit: Mapped["IngredientUnitModel"] = orm.relationship("IngredientUnitModel", back_populates="aliases")

    name: Mapped[str] = mapped_column(String)

    # Automatically updated by sqlalchemy event, do not write to this manually
    name_normalized: Mapped[str | None] = mapped_column(sa.String, index=True)

    @auto_init()
    def __init__(self, session: Session, name: str, **_) -> None:
        self.name_normalized = self.normalize(name)
        tableargs = [
            sa.Index(
                "ix_ingredient_units_aliases_name_normalized",
                "name_normalized",
                unique=False,
            ),
        ]

        if session.get_bind().name == "postgresql":
            tableargs.extend(
                [
                    sa.Index(
                        "ix_ingredient_units_aliases_name_normalized_gin",
                        "name_normalized",
                        unique=False,
                        postgresql_using="gin",
                        postgresql_ops={
                            "name_normalized": "gin_trgm_ops",
                        },
                    ),
                ]
            )

        self.__table_args__ = tableargs


class IngredientFoodAliasModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ingredient_foods_aliases"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    food_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("ingredient_foods.id"), primary_key=True)
    food: Mapped["IngredientFoodModel"] = orm.relationship("IngredientFoodModel", back_populates="aliases")

    name: Mapped[str] = mapped_column(String)

    # Automatically updated by sqlalchemy event, do not write to this manually
    name_normalized: Mapped[str | None] = mapped_column(sa.String, index=True)

    @auto_init()
    def __init__(self, session: Session, name: str, **_) -> None:
        self.name_normalized = self.normalize(name)
        tableargs = [
            sa.Index(
                "ix_ingredient_foods_aliases_name_normalized",
                "name_normalized",
                unique=False,
            ),
        ]

        if session.get_bind().name == "postgresql":
            tableargs.extend(
                [
                    sa.Index(
                        "ix_ingredient_foods_aliases_name_normalized_gin",
                        "name_normalized",
                        unique=False,
                        postgresql_using="gin",
                        postgresql_ops={
                            "name_normalized": "gin_trgm_ops",
                        },
                    ),
                ]
            )

        self.__table_args__ = tableargs


class RecipeIngredientModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipes_ingredients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    position: Mapped[int | None] = mapped_column(Integer, index=True)
    recipe_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"))

    title: Mapped[str | None] = mapped_column(String)  # Section Header - Shows if Present
    note: Mapped[str | None] = mapped_column(String)  # Force Show Text - Overrides Concat

    # Scaling Items
    unit_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("ingredient_units.id"), index=True)
    unit: Mapped[IngredientUnitModel | None] = orm.relationship(IngredientUnitModel, uselist=False)

    food_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("ingredient_foods.id"), index=True)
    food: Mapped[IngredientFoodModel | None] = orm.relationship(IngredientFoodModel, uselist=False)
    quantity: Mapped[float | None] = mapped_column(Float)

    original_text: Mapped[str | None] = mapped_column(String)

    reference_id: Mapped[GUID | None] = mapped_column(GUID)  # Reference Links

    # Automatically updated by sqlalchemy event, do not write to this manually
    note_normalized: Mapped[str | None] = mapped_column(String, index=True)
    original_text_normalized: Mapped[str | None] = mapped_column(String, index=True)

    @auto_init()
    def __init__(
        self,
        session: Session,
        note: str | None = None,
        orginal_text: str | None = None,
        **_,
    ) -> None:
        # SQLAlchemy events do not seem to register things that are set during auto_init
        if note is not None:
            self.note_normalized = self.normalize(note)

        if orginal_text is not None:
            self.orginal_text = self.normalize(orginal_text)

        tableargs = [  # base set of indices
            sa.Index(
                "ix_recipes_ingredients_note_normalized",
                "note_normalized",
                unique=False,
            ),
            sa.Index(
                "ix_recipes_ingredients_original_text_normalized",
                "original_text_normalized",
                unique=False,
            ),
        ]
        if session.get_bind().name == "postgresql":
            tableargs.extend(
                [
                    sa.Index(
                        "ix_recipes_ingredients_note_normalized_gin",
                        "note_normalized",
                        unique=False,
                        postgresql_using="gin",
                        postgresql_ops={
                            "note_normalized": "gin_trgm_ops",
                        },
                    ),
                    sa.Index(
                        "ix_recipes_ingredients_original_text_normalized_gin",
                        "original_text",
                        unique=False,
                        postgresql_using="gin",
                        postgresql_ops={
                            "original_text_normalized": "gin_trgm_ops",
                        },
                    ),
                ]
            )
        # add indices
        self.__table_args__ = tuple(tableargs)


@event.listens_for(IngredientUnitModel.name, "set")
def receive_unit_name(target: IngredientUnitModel, value: str | None, oldvalue, initiator):
    if value is not None:
        target.name_normalized = IngredientUnitModel.normalize(value)
    else:
        target.name_normalized = None


@event.listens_for(IngredientUnitModel.plural_name, "set")
def receive_plural_unit_name(target: IngredientUnitModel, value: str | None, oldvalue, initiator):
    if value is not None:
        target.plural_name_normalized = IngredientUnitModel.normalize(value)
    else:
        target.plural_name_normalized = None


@event.listens_for(IngredientUnitModel.abbreviation, "set")
def receive_unit_abbreviation(target: IngredientUnitModel, value: str | None, oldvalue, initiator):
    if value is not None:
        target.abbreviation_normalized = IngredientUnitModel.normalize(value)
    else:
        target.abbreviation_normalized = None


@event.listens_for(IngredientUnitModel.plural_abbreviation, "set")
def receive_unit_plural_abbreviation(target: IngredientUnitModel, value: str | None, oldvalue, initiator):
    if value is not None:
        target.plural_abbreviation_normalized = IngredientUnitModel.normalize(value)
    else:
        target.plural_abbreviation_normalized = None


@event.listens_for(IngredientFoodModel.name, "set")
def receive_food_name(target: IngredientFoodModel, value: str | None, oldvalue, initiator):
    if value is not None:
        target.name_normalized = IngredientFoodModel.normalize(value)
    else:
        target.name_normalized = None


@event.listens_for(IngredientFoodModel.plural_name, "set")
def receive_food_plural_name(target: IngredientFoodModel, value: str | None, oldvalue, initiator):
    if value is not None:
        target.plural_name_normalized = IngredientFoodModel.normalize(value)
    else:
        target.plural_name_normalized = None


@event.listens_for(IngredientUnitAliasModel.name, "set")
def receive_unit_alias_name(target: IngredientUnitAliasModel, value: str, oldvalue, initiator):
    target.name_normalized = IngredientUnitAliasModel.normalize(value)


@event.listens_for(IngredientFoodAliasModel.name, "set")
def receive_food_alias_name(target: IngredientFoodAliasModel, value: str, oldvalue, initiator):
    target.name_normalized = IngredientFoodAliasModel.normalize(value)


@event.listens_for(RecipeIngredientModel.note, "set")
def receive_ingredient_note(target: RecipeIngredientModel, value: str | None, oldvalue, initiator):
    if value is not None:
        target.note_normalized = RecipeIngredientModel.normalize(value)
    else:
        target.note_normalized = None


@event.listens_for(RecipeIngredientModel.original_text, "set")
def receive_ingredient_original_text(target: RecipeIngredientModel, value: str | None, oldvalue, initiator):
    if value is not None:
        target.original_text_normalized = RecipeIngredientModel.normalize(value)
    else:
        target.original_text_normalized = None
