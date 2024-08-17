from abc import ABC, abstractmethod

from fastapi import Response
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories


class ABCMultiTenantTestCase(ABC):
    def __init__(self, database: AllRepositories, client: TestClient) -> None:
        self.database = database
        self.client = client
        self.items: list = []

    @abstractmethod
    def seed_action(self, group_id: str) -> set[int] | set[str]: ...

    @abstractmethod
    def seed_multi(self, group1_id: str, group2_id: str) -> tuple[set[str], set[str]]: ...

    @abstractmethod
    def get_all(self, token: str) -> Response: ...

    @abstractmethod
    def cleanup(self) -> None: ...

    def __enter__(self):  # noqa: B027
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
