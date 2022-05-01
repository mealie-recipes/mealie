from mealie.repos.repository_factory import AllRepositories
from mealie.repos.seed.seeders import IngredientFoodsSeeder, IngredientUnitsSeeder, MultiPurposeLabelSeeder
from mealie.schema.user.user import GroupInDB, PrivateUser
from mealie.services._base_service import BaseService


class SeederService(BaseService):
    def __init__(self, repos: AllRepositories, user: PrivateUser, group: GroupInDB):
        self.repos = repos
        self.user = user
        self.group = group
        super().__init__()

    def seed_foods(self, locale: str) -> None:
        seeder = IngredientFoodsSeeder(self.repos, self.logger, self.group.id)
        seeder.seed(locale)

    def seed_labels(self, locale: str) -> None:
        seeder = MultiPurposeLabelSeeder(self.repos, self.logger, self.group.id)
        seeder.seed(locale)

    def seed_units(self, locale: str) -> None:
        seeder = IngredientUnitsSeeder(self.repos, self.logger, self.group.id)
        seeder.seed(locale)
