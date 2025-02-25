from collections.abc import Iterable
from typing import cast
from uuid import UUID

from pydantic import UUID4
from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models.household import Household, HouseholdToRecipe
from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.tag import Tag
from mealie.db.models.recipe.tool import Tool
from mealie.db.models.users.users import User
from mealie.repos.repository_generic import GroupRepositoryGeneric, HouseholdRepositoryGeneric
from mealie.schema.household import (
    HouseholdCreate,
    HouseholdInDB,
    HouseholdRecipeOut,
    HouseholdStatistics,
    UpdateHousehold,
)


class RepositoryHousehold(GroupRepositoryGeneric[HouseholdInDB, Household]):
    def create(self, data: HouseholdCreate | dict) -> HouseholdInDB:
        if isinstance(data, HouseholdCreate):
            data = data.model_dump()

        if not data.get("group_id"):
            data["group_id"] = self.group_id
        max_attempts = 10
        original_name = cast(str, data["name"])

        attempts = 0
        while True:
            try:
                data["slug"] = slugify(data["name"])
                return super().create(data)
            except IntegrityError:
                self.session.rollback()
                attempts += 1
                if attempts >= max_attempts:
                    raise

                data["name"] = f"{original_name} ({attempts})"

    def create_many(self, data: Iterable[HouseholdInDB | dict]) -> list[HouseholdInDB]:
        # since create uses special logic for resolving slugs, we don't want to use the standard create_many method
        return [self.create(new_household) for new_household in data]

    def update(self, match_value: str | int | UUID4, new_data: UpdateHousehold | dict) -> HouseholdInDB:
        if isinstance(new_data, HouseholdCreate):
            new_data.slug = slugify(new_data.name)
        else:
            new_data["slug"] = slugify(new_data["name"])

        return super().update(match_value, new_data)

    def update_many(self, data: Iterable[UpdateHousehold | dict]) -> list[HouseholdInDB]:
        # since update uses special logic for resolving slugs, we don't want to use the standard update_many method
        return [
            self.update(household["id"] if isinstance(household, dict) else household.id, household)
            for household in data
        ]

    def get_by_name(self, name: str) -> HouseholdInDB | None:
        if not self.group_id:
            raise Exception("group_id not set")
        dbhousehold = (
            self.session.execute(select(self.model).filter_by(name=name, group_id=self.group_id))
            .scalars()
            .one_or_none()
        )
        if dbhousehold is None:
            return None
        return self.schema.model_validate(dbhousehold)

    def get_by_slug_or_id(self, slug_or_id: str | UUID) -> HouseholdInDB | None:
        if isinstance(slug_or_id, str):
            try:
                slug_or_id = UUID(slug_or_id)
            except ValueError:
                pass

        if isinstance(slug_or_id, UUID):
            return self.get_one(slug_or_id)
        else:
            return self.get_one(slug_or_id, key="slug")

    def statistics(self, group_id: UUID4, household_id: UUID4) -> HouseholdStatistics:
        def model_count(model: type[SqlAlchemyBase], *, filter_household: bool = True) -> int:
            stmt = select(func.count(model.id)).filter_by(group_id=group_id)
            if filter_household:
                stmt = stmt.filter_by(household_id=household_id)
            return self.session.scalar(stmt)

        return HouseholdStatistics(
            # household-level statistics
            total_recipes=model_count(RecipeModel),
            total_users=model_count(User),
            # group-level statistics
            total_categories=model_count(Category, filter_household=False),
            total_tags=model_count(Tag, filter_household=False),
            total_tools=model_count(Tool, filter_household=False),
        )


class RepositoryHouseholdRecipes(HouseholdRepositoryGeneric[HouseholdRecipeOut, HouseholdToRecipe]):
    def get_by_recipe(self, recipe_id: UUID4) -> HouseholdRecipeOut | None:
        if not self.household_id:
            raise Exception("household_id not set")

        stmt = select(HouseholdToRecipe).filter(
            HouseholdToRecipe.household_id == self.household_id, HouseholdToRecipe.recipe_id == recipe_id
        )
        result = self.session.execute(stmt).scalars().one_or_none()
        return None if result is None else self.schema.model_validate(result)
