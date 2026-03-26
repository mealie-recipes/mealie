import json
from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path

from mealie.core.root_logger import get_logger
from mealie.repos.repository_factory import AllRepositories


class AbstractSeeder(ABC):
    """
    Abstract class for seeding data.
    """

    resources = Path(__file__).parent / "resources"

    def __init__(self, db: AllRepositories, logger: Logger | None = None):
        """
        Initialize the abstract seeder.
        :param db_conn: Database connection.
        :param logger: Logger.
        """
        self.repos = db
        self.logger = logger or get_logger("Data Seeder")

    @classmethod
    @abstractmethod
    def get_file(self, locale: str | None = None) -> Path: ...

    @classmethod
    def load_file(self, file: Path) -> dict[str, dict]:
        return json.loads(file.read_text(encoding="utf-8"))

    @abstractmethod
    def seed(self, locale: str | None = None) -> None: ...
