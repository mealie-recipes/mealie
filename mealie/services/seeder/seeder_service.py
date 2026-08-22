from mealie.repos.repository_factory import AllRepositories
from mealie.repos.seed.seeders import IngredientFoodsSeeder, IngredientUnitsSeeder
from mealie.services._base_service import BaseService


class SeederService(BaseService):
    def __init__(self, repos: AllRepositories):
        self.repos = repos
        super().__init__()

    def seed_foods(self, locale: str) -> None:
        """Seeds foods along with the labels that group them."""
        seeder = IngredientFoodsSeeder(self.repos, self.logger)
        seeder.seed(locale)

    def seed_units(self, locale: str) -> None:
        seeder = IngredientUnitsSeeder(self.repos, self.logger)
        seeder.seed(locale)
