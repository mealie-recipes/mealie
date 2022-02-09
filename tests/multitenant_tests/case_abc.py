from abc import ABC, abstractmethod

from fastapi import Response
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories


class ABCMultiTenanatTestCase(ABC):
    def __init__(self, database: AllRepositories, client: TestClient) -> None:
        self.database = database
        self.client = client

    @abstractmethod
    def seed_action(repos: AllRepositories, group_id: str) -> set[int] | set[str]:
        ...

    @abstractmethod
    def get_all(token: str) -> Response:
        ...
