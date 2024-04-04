from abc import ABC, abstractmethod
from pathlib import Path
from urllib import parse as urlparse

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AbstractDBProvider(ABC):
    @property
    @abstractmethod
    def db_url(self) -> str: ...

    @property
    @abstractmethod
    def db_url_public(self) -> str: ...


class SQLiteProvider(AbstractDBProvider, BaseModel):
    data_dir: Path
    prefix: str = ""

    @property
    def db_path(self):
        return self.data_dir / f"{self.prefix}mealie.db"

    @property
    def db_url(self) -> str:
        return f"sqlite:///{str(self.db_path.absolute())}"

    @property
    def db_url_public(self) -> str:
        return self.db_url


class PostgresProvider(AbstractDBProvider, BaseSettings):
    POSTGRES_USER: str = "mealie"
    POSTGRES_PASSWORD: str = "mealie"
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "mealie"
    POSTGRES_URL_OVERRIDE: str | None = None

    model_config = SettingsConfigDict(arbitrary_types_allowed=True, extra="allow")

    @property
    def db_url(self) -> str:
        if self.POSTGRES_URL_OVERRIDE:
            url = PostgresDsn(url=self.POSTGRES_URL_OVERRIDE)
            if not url.scheme == ("postgresql"):
                raise ValueError("POSTGRES_URL_OVERRIDE scheme must be postgresql")

            return str(url)

        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=self.POSTGRES_USER,
                password=urlparse.quote_plus(self.POSTGRES_PASSWORD),
                host=f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}",
                path=f"{self.POSTGRES_DB or ''}",
            )
        )

    @property
    def db_url_public(self) -> str:
        user = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        return self.db_url.replace(user, "*****", 1).replace(password, "*****", 1)


def db_provider_factory(provider_name: str, data_dir: Path, env_file: Path, env_encoding="utf-8") -> AbstractDBProvider:
    if provider_name == "postgres":
        return PostgresProvider(_env_file=env_file, _env_file_encoding=env_encoding)
    else:
        return SQLiteProvider(data_dir=data_dir)
