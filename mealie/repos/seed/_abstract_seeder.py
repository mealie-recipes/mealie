from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path

from mealie.core.root_logger import get_logger
from mealie.repos.repository_factory import AllRepositories


class AbstractSeeder(ABC):
    """
    Abstract class for seeding data.
    """

    def __init__(self, db: AllRepositories, logger: Logger | None = None):
        """
        Initialize the abstract seeder.
        :param db_conn: Database connection.
        :param logger: Logger.
        """
        self.repos = db
        self.logger = logger or get_logger("Data Seeder")
        self.resources = Path(__file__).parent / "resources"

    @abstractmethod
    def seed(self, locale: str | None = None) -> None: ...
