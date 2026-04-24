import json
import pathlib
from logging import Logger

from slugify import slugify

from mealie.lang.providers import Translator
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.household import HouseholdInDB
from mealie.schema.recipe import Recipe
from mealie.schema.user.user import PrivateUser
from mealie.services.recipe.recipe_service import RecipeService

from ._abstract_seeder import AbstractSeeder


class StarterRecipeSeeder(AbstractSeeder):
    def __init__(
        self,
        db: AllRepositories,
        user: PrivateUser,
        household: HouseholdInDB,
        translator: Translator,
        logger: Logger | None = None,
    ):
        super().__init__(db, logger)
        self.user = user
        self.household = household
        self.recipe_service = RecipeService(db, user, household, translator)

    @classmethod
    def get_file(cls, locale: str | None = None) -> pathlib.Path:
        return cls.resources / "recipes" / "starter_recipes.json"

    @classmethod
    def load_catalog(cls) -> list[dict]:
        return json.loads(cls.get_file().read_text(encoding="utf-8"))

    def seed(self, locale: str | None = None) -> None:
        if self.repos.recipes.get_all(limit=1):
            self.logger.info("Starter recipes already exist for this group; skipping")
            return

        recipes = self.load_catalog()
        self.logger.info(f"Seeding {len(recipes)} starter recipes")

        created = 0
        for recipe in recipes:
            try:
                tags = [
                    {
                        "name": tag,
                        "slug": slugify(tag),
                    }
                    for tag in recipe.get("tags", [])
                ]
                cleaned_recipe = self.recipe_service.clean_recipe_dict(
                    {
                        "name": recipe["name"],
                        "tags": tags,
                    }
                )
                self.recipe_service.create_one(Recipe(**cleaned_recipe))
                created += 1
            except Exception as exc:
                self.logger.error(f"Failed to seed starter recipe '{recipe.get('name', '')}': {exc}")

        self.logger.info(f"Seeded {created} starter recipes")
