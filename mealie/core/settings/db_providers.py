from abc import ABC, abstractproperty
from pathlib import Path

from pydantic import BaseModel, BaseSettings, PostgresDsn


class AbstractDBProvider(ABC):
    @abstractproperty
    def db_url(self) -> str:
        pass

    @property
    def db_url_public(self) -> str:
        pass


class SQLiteProvider(AbstractDBProvider, BaseModel):
    data_dir: Path
    prefix: str = ""

    @property
    def db_path(self):
        return self.data_dir / f"{self.prefix}mealie.db"

    @property
    def db_url(self) -> str:
        return "sqlite:///" + str(self.db_path.absolute())

    @property
    def db_url_public(self) -> str:
        return self.db_url


class PostgresProvider(AbstractDBProvider, BaseSettings):
    POSTGRES_USER: str = "mealie"
    POSTGRES_PASSWORD: str = "mealie"
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: str = 5432
    POSTGRES_DB: str = "mealie"

    @property
    def db_url(self) -> str:
        host = f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}"
        return PostgresDsn.build(
            scheme="postgresql",
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=host,
            path=f"/{self.POSTGRES_DB or ''}",
        )

    @property
    def db_url_public(self) -> str:
        user = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        return self.db_url.replace(user, "*****", 1).replace(password, "*****", 1)


def db_provider_factory(provider_name: str, data_dir: Path, env_file: Path, env_encoding="utf-8") -> AbstractDBProvider:
    if provider_name == "postgres":
        return PostgresProvider(_env_file=env_file, _env_file_encoding=env_encoding)
    elif provider_name == "sqlite":
        return SQLiteProvider(data_dir=data_dir)
    else:
        return
