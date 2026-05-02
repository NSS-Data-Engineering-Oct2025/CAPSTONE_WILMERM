"""Centralized configuration — all environment variables are read here and nowhere else."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    host: str = field(default_factory=lambda: os.environ["POSTGRES_HOST"])
    port: int = field(default_factory=lambda: int(os.environ.get("POSTGRES_PORT", "5432")))
    dbname: str = field(default_factory=lambda: os.environ["POSTGRES_DB"])
    user: str = field(default_factory=lambda: os.environ["POSTGRES_USER"])
    password: str = field(default_factory=lambda: os.environ["POSTGRES_PASSWORD"])

    @property
    def connection_string(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password}"


@dataclass(frozen=True)
class ApiKeys:
    epa_airnow: str = field(default_factory=lambda: os.environ["EPA_AIRNOW_API_KEY"])
    usda: str = field(default_factory=lambda: os.environ["USDA_API_KEY"])
    census: str = field(default_factory=lambda: os.environ.get("CENSUS_API_KEY", ""))


db_config = DatabaseConfig()
api_keys = ApiKeys()
