from typing import TYPE_CHECKING

import sqlalchemy as sa
from pydantic import ConfigDict
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, event, orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.session import Session

from mealie.db.models._model_base import BaseMixins, FilterableColumn, SqlAlchemyBase
from mealie.db.models.recipe.api_extras import IngredientFoodExtras, api_extras
from mealie.db.models.recipe.labels import MultiPurposeLabel

from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..group import Group
    from ..household import Household
    from .recipe import RecipeModel

households_to_ingredient_foods = sa.Table(
    "households_to_ingredient_foods",
    SqlAlchemyBase.metadata,
    sa.Column("household_id", GUID, sa.ForeignKey("households.id"), index=True),
    sa.Column("food_id", GUID, sa.ForeignKey("ingredient_foods.id"), index=True),
    sa.UniqueConstraint("household_id", "food_id", name="household_id_food_id_key"),
)


def resolve_substitutions(
    session: Session,
    group_id: GUID | None,
    substitutions: list[dict] | None,
    exclude_food_id: GUID | None = None,
) -> list[tuple[GUID | None, str | None]]:
    """
    Normalizes a substitution payload into (substitute_food_id, note) pairs safe to persist.

    Substitute ids arrive straight from the payload, so the repository's group scoping does
    not cover them. They are resolved against `group_id`, and an id resolving to nothing --
    deleted, or belonging to another group -- invalidates the whole substitution, since the note
    qualifies the food it travels with. `exclude_food_id` rejects self-substitution the same
    way. Both tiers share this; only the row they build from it differs.
    """

    if not substitutions or not group_id:
        return []

    requested_food_ids = {sub.get("substitute_food_id") for sub in substitutions}
    requested_food_ids.discard(None)

    resolvable_food_ids: set = set()
    if requested_food_ids:
        resolvable_food_ids = set(
            session.execute(
                sa.select(IngredientFoodModel.id).filter(
                    IngredientFoodModel.group_id == group_id,
                    IngredientFoodModel.id.in_(requested_food_ids),
                )
            )
            .scalars()
            .all()
        )

    resolved: list[tuple[GUID | None, str | None]] = []
    seen_food_ids: set = set()
    for sub in substitutions:
        substitute_food_id = sub.get("substitute_food_id")
        note = (sub.get("note") or "").strip() or None

        if substitute_food_id is None:
            # note-only rows are deliberately not de-duped: two textual workarounds are
            # two legitimate rows, and there is no id to collapse them on
            if not note:
                continue
        else:
            if substitute_food_id not in resolvable_food_ids or substitute_food_id == exclude_food_id:
                continue

            if substitute_food_id in seen_food_ids:
                continue

            seen_food_ids.add(substitute_food_id)

        resolved.append((substitute_food_id, note))

    return resolved


class IngredientUnitModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ingredient_units"
    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    # ID Relationships
    group_id: FilterableColumn[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="ingredient_units", foreign_keys=[group_id])

    name: FilterableColumn[str | None] = mapped_column(String)
    plural_name: FilterableColumn[str | None] = mapped_column(String)
    description: FilterableColumn[str | None] = mapped_column(String)
    abbreviation: FilterableColumn[str | None] = mapped_column(String)
    plural_abbreviation: FilterableColumn[str | None] = mapped_column(String)
    use_abbreviation: FilterableColumn[bool | None] = mapped_column(Boolean, default=False)
    fraction: FilterableColumn[bool | None] = mapped_column(Boolean, default=True)

    ingredients: Mapped[list["RecipeIngredientModel"]] = orm.relationship(
        "RecipeIngredientModel", back_populates="unit"
    )
    aliases: Mapped[list["IngredientUnitAliasModel"]] = orm.relationship(
        "IngredientUnitAliasModel",
        back_populates="unit",
        cascade="all, delete, delete-orphan",
    )

    # Standardization
    standard_quantity: FilterableColumn[float | None] = mapped_column(Float)
    standard_unit: FilterableColumn[str | None] = mapped_column(String)

    # Automatically updated by sqlalchemy event, do not write to this manually
    name_normalized: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    plural_name_normalized: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    abbreviation_normalized: FilterableColumn[str | None] = mapped_column(String, index=True)
    plural_abbreviation_normalized: FilterableColumn[str | None] = mapped_column(String, index=True)

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
    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    # ID Relationships
    group_id: FilterableColumn[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="ingredient_foods", foreign_keys=[group_id])
    households_with_ingredient_food: Mapped[list["Household"]] = orm.relationship(
        "Household", secondary=households_to_ingredient_foods, back_populates="ingredient_foods_on_hand"
    )

    name: FilterableColumn[str | None] = mapped_column(String)
    plural_name: FilterableColumn[str | None] = mapped_column(String)
    description: FilterableColumn[str | None] = mapped_column(String)

    ingredients: Mapped[list["RecipeIngredientModel"]] = orm.relationship(
        "RecipeIngredientModel", back_populates="food"
    )
    aliases: Mapped[list["IngredientFoodAliasModel"]] = orm.relationship(
        "IngredientFoodAliasModel",
        back_populates="food",
        cascade="all, delete, delete-orphan",
    )
    # substitutions this food offers, e.g. chicken stock -> chicken broth
    substitutions: Mapped[list["IngredientFoodSubstitutionModel"]] = orm.relationship(
        "IngredientFoodSubstitutionModel",
        back_populates="food",
        foreign_keys="IngredientFoodSubstitutionModel.food_id",
        cascade="all, delete, delete-orphan",
        order_by="IngredientFoodSubstitutionModel.position",
        collection_class=ordering_list("position"),
    )
    # substitutions pointing at this food; exists so deleting a food cleans up the ones aimed at it
    substitution_references: Mapped[list["IngredientFoodSubstitutionModel"]] = orm.relationship(
        "IngredientFoodSubstitutionModel",
        back_populates="substitute_food",
        foreign_keys="IngredientFoodSubstitutionModel.substitute_food_id",
        cascade="all, delete, delete-orphan",
    )
    extras: Mapped[list[IngredientFoodExtras]] = orm.relationship("IngredientFoodExtras", cascade="all, delete-orphan")

    label_id: FilterableColumn[GUID | None] = mapped_column(GUID, ForeignKey("multi_purpose_labels.id"), index=True)
    label: Mapped[MultiPurposeLabel | None] = orm.relationship(MultiPurposeLabel, uselist=False, back_populates="foods")

    # Automatically updated by sqlalchemy event, do not write to this manually
    name_normalized: FilterableColumn[str | None] = mapped_column(sa.String, index=True)
    plural_name_normalized: FilterableColumn[str | None] = mapped_column(sa.String, index=True)

    model_config = ConfigDict(
        exclude={
            "households_with_ingredient_food",
            # substitutions are resolved explicitly, since auto_init creates rows it can't find
            "substitutions",
        }
    )

    # Deprecated
    on_hand: Mapped[bool] = mapped_column(Boolean, default=False)

    def _set_substitutions(self, session: Session, group_id: GUID, substitutions: list[dict] | None) -> None:
        """
        Builds the substitution rows by hand, since auto_init creates any related row it
        fails to look up and would manufacture a food out of an unrecognized id.
        """

        resolved = resolve_substitutions(session, group_id, substitutions, exclude_food_id=self.id)
        if not resolved:
            self.substitutions = []
            return

        # Existing rows are reused rather than rebuilt. SQLAlchemy inserts before it deletes
        # within a single flush, so replacing the collection wholesale would insert a copy of
        # a row still on its way out and trip the (food_id, substitute_food_id) constraint.
        reusable_by_food_id = {row.substitute_food_id: row for row in self.substitutions if row.substitute_food_id}
        reusable_note_only = [row for row in self.substitutions if not row.substitute_food_id]

        rows: list[IngredientFoodSubstitutionModel] = []
        for substitute_food_id, note in resolved:
            if substitute_food_id is not None:
                row = reusable_by_food_id.get(substitute_food_id)
            else:
                row = reusable_note_only.pop(0) if reusable_note_only else None

            if row is None:
                row = IngredientFoodSubstitutionModel(substitute_food_id=substitute_food_id, note=note)
            else:
                row.substitute_food_id = substitute_food_id
                row.note = note

            rows.append(row)

        # rows left over are orphaned by the assignment and cascade-deleted
        self.substitutions = rows

    @api_extras
    @auto_init()
    def __init__(
        self,
        session: Session,
        group_id: GUID,
        name: str | None = None,
        plural_name: str | None = None,
        households_with_ingredient_food: list[str] | None = None,
        substitutions: list[dict] | None = None,
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

        self._set_substitutions(session, group_id, substitutions)

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
    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    unit_id: FilterableColumn[GUID] = mapped_column(GUID, ForeignKey("ingredient_units.id"), primary_key=True)
    unit: Mapped["IngredientUnitModel"] = orm.relationship("IngredientUnitModel", back_populates="aliases")

    name: FilterableColumn[str] = mapped_column(String)

    # Automatically updated by sqlalchemy event, do not write to this manually
    name_normalized: FilterableColumn[str | None] = mapped_column(sa.String, index=True)

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
    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    food_id: FilterableColumn[GUID] = mapped_column(GUID, ForeignKey("ingredient_foods.id"), primary_key=True)
    food: Mapped["IngredientFoodModel"] = orm.relationship("IngredientFoodModel", back_populates="aliases")

    name: FilterableColumn[str] = mapped_column(String)

    # Automatically updated by sqlalchemy event, do not write to this manually
    name_normalized: FilterableColumn[str | None] = mapped_column(sa.String, index=True)

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


class IngredientFoodSubstitutionModel(SqlAlchemyBase, BaseMixins):
    """
    A directed "this food may be replaced by that one" substitution.

    Both the substitute food and the note are optional, but at least one must be
    present: a substitution can be another food ("chicken broth"), a free-text
    workaround ("water and a bouillon cube"), or a food with a caveat attached.
    """

    __tablename__ = "ingredient_foods_substitutions"
    __table_args__ = (
        sa.UniqueConstraint("food_id", "substitute_food_id", name="ingredient_foods_substitutions_food_ids_key"),
        sa.CheckConstraint("food_id != substitute_food_id", name="ingredient_foods_substitutions_no_self_substitution"),
        sa.CheckConstraint(
            "substitute_food_id IS NOT NULL OR note IS NOT NULL",
            name="ingredient_foods_substitutions_food_or_note",
        ),
    )

    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    food_id: FilterableColumn[GUID] = mapped_column(GUID, ForeignKey("ingredient_foods.id"), index=True, nullable=False)
    food: Mapped["IngredientFoodModel"] = orm.relationship(
        "IngredientFoodModel", back_populates="substitutions", foreign_keys=[food_id]
    )

    substitute_food_id: FilterableColumn[GUID | None] = mapped_column(
        GUID, ForeignKey("ingredient_foods.id"), index=True
    )
    substitute_food: Mapped["IngredientFoodModel | None"] = orm.relationship(
        "IngredientFoodModel", back_populates="substitution_references", foreign_keys=[substitute_food_id]
    )

    note: FilterableColumn[str | None] = mapped_column(String)

    # note-only substitutions have no name to sort by, so display order is stored
    position: FilterableColumn[int | None] = mapped_column(Integer, index=True)


class RecipeIngredientModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipes_ingredients"
    id: FilterableColumn[int] = mapped_column(Integer, primary_key=True)
    position: FilterableColumn[int | None] = mapped_column(Integer, index=True)
    recipe_id: FilterableColumn[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"))

    title: FilterableColumn[str | None] = mapped_column(String)  # Section Header - Shows if Present
    note: FilterableColumn[str | None] = mapped_column(String)  # Force Show Text - Overrides Concat

    # Scaling Items
    unit_id: FilterableColumn[GUID | None] = mapped_column(GUID, ForeignKey("ingredient_units.id"), index=True)
    unit: Mapped[IngredientUnitModel | None] = orm.relationship(IngredientUnitModel, uselist=False)

    food_id: FilterableColumn[GUID | None] = mapped_column(GUID, ForeignKey("ingredient_foods.id"), index=True)
    food: Mapped[IngredientFoodModel | None] = orm.relationship(IngredientFoodModel, uselist=False)
    quantity: FilterableColumn[float | None] = mapped_column(Float)

    original_text: FilterableColumn[str | None] = mapped_column(String)

    reference_id: FilterableColumn[GUID | None] = mapped_column(GUID)  # Reference Links

    # Recipe Reference
    referenced_recipe_id: FilterableColumn[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"), index=True)
    referenced_recipe: Mapped["RecipeModel"] = orm.relationship(
        "RecipeModel", back_populates="referenced_ingredients", foreign_keys=[referenced_recipe_id]
    )

    substitutions: Mapped[list["RecipeIngredientSubstitutionModel"]] = orm.relationship(
        "RecipeIngredientSubstitutionModel",
        back_populates="ingredient",
        cascade="all, delete, delete-orphan",
        order_by="RecipeIngredientSubstitutionModel.position",
        collection_class=ordering_list("position"),
    )

    # Automatically updated by sqlalchemy event, do not write to this manually
    note_normalized: FilterableColumn[str | None] = mapped_column(String, index=True)
    original_text_normalized: FilterableColumn[str | None] = mapped_column(String, index=True)

    model_config = ConfigDict(
        exclude={
            "id",
            # substitutions are resolved explicitly, since auto_init creates rows it can't find
            "substitutions",
        }
    )

    def _set_substitutions(self, session: Session, group_id: GUID | None, substitutions: list[dict] | None) -> None:
        """
        Builds the substitution rows by hand, since auto_init creates any related row it
        fails to look up and would manufacture a food out of an unrecognized id.

        Rows are always built fresh rather than reused, unlike the food tier: ingredient rows
        are destroyed and recreated on every recipe save, so there is never an existing set to
        reconcile with, and no unique constraint for a re-insert to collide with.
        """

        self.substitutions = [
            RecipeIngredientSubstitutionModel(substitute_food_id=substitute_food_id, note=note)
            for substitute_food_id, note in resolve_substitutions(session, group_id, substitutions)
        ]

    @auto_init()
    def __init__(
        self,
        session: Session,
        note: str | None = None,
        orginal_text: str | None = None,
        group_id: GUID | None = None,
        substitutions: list[dict] | None = None,
        **_,
    ) -> None:
        # SQLAlchemy events do not seem to register things that are set during auto_init
        if note is not None:
            self.note_normalized = self.normalize(note)

        if orginal_text is not None:
            self.orginal_text = self.normalize(orginal_text)

        self._set_substitutions(session, group_id, substitutions)

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


class RecipeIngredientSubstitutionModel(SqlAlchemyBase, BaseMixins):
    """
    A substitution scoped to one ingredient line on one recipe.

    Structurally identical to IngredientFoodSubstitutionModel, but the left side is an
    ingredient row rather than a food. There is no unique constraint: ingredient rows are
    rebuilt from scratch on every recipe save, so the write path always starts from an
    empty set and deduping happens in the schema.
    """

    __tablename__ = "recipes_ingredients_substitutions"
    __table_args__ = (
        sa.CheckConstraint(
            "substitute_food_id IS NOT NULL OR note IS NOT NULL",
            name="recipes_ingredients_substitutions_food_or_note",
        ),
    )

    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    # Integer, because recipes_ingredients.id is an autoincrement integer PK
    ingredient_id: FilterableColumn[int] = mapped_column(
        Integer, ForeignKey("recipes_ingredients.id"), index=True, nullable=False
    )
    ingredient: Mapped["RecipeIngredientModel"] = orm.relationship(
        "RecipeIngredientModel", back_populates="substitutions"
    )

    substitute_food_id: FilterableColumn[GUID | None] = mapped_column(
        GUID, ForeignKey("ingredient_foods.id"), index=True
    )
    substitute_food: Mapped["IngredientFoodModel | None"] = orm.relationship("IngredientFoodModel")

    note: FilterableColumn[str | None] = mapped_column(String)

    # note-only substitutions have no name to sort by, so display order is stored
    position: FilterableColumn[int | None] = mapped_column(Integer, index=True)


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
