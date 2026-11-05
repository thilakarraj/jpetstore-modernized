"""Application configuration from environment variables."""

from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

ALEMBIC_INI_DEFAULT_URL = "driver://user:pass@localhost/dbname"

# Tables required before ``seed_catalog`` / checkout concurrency tests on MySQL.
MYSQL_SEED_REQUIRED_TABLES: tuple[str, ...] = (
    "category",
    "supplier",
    "bannerdata",
    "product",
    "item",
    "inventory",
    "sequence",
)


class Settings(BaseSettings):
    """Central settings; loaded once via dependency injection."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = Field(
        default="mysql+pymysql://jpetstore_app:jpetstore@127.0.0.1:3306/jpetstore?charset=utf8mb4",
        alias="DATABASE_URL",
    )
    test_database_url: str = Field(default="", alias="TEST_DATABASE_URL")

    jwt_secret: str = Field(
        default="change-me-use-at-least-32-random-bytes-in-production",
        min_length=32,
        alias="JWT_SECRET",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_issuer: str = Field(default="jpetstore", alias="JWT_ISSUER")
    jwt_audience: str = Field(default="jpetstore-api", alias="JWT_AUDIENCE")
    jwt_expire_minutes: int = Field(default=60, alias="JWT_EXPIRE_MINUTES")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_dir: str = Field(default="./logs", alias="LOG_DIR")
    log_retention_days: int = Field(default=30, alias="LOG_RETENTION_DAYS")
    log_rotation: Literal["midnight"] = Field(default="midnight", alias="LOG_ROTATION")
    log_json: bool = Field(default=True, alias="LOG_JSON")

    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:8000",
        alias="CORS_ORIGINS",
    )

    metrics_protect: bool = Field(default=False, alias="METRICS_PROTECT")
    metrics_username: str = Field(default="", alias="METRICS_USERNAME")
    metrics_password: str = Field(default="", alias="METRICS_PASSWORD")

    rate_limit_login_per_minute: int = Field(default=10, alias="RATE_LIMIT_LOGIN_PER_MINUTE")
    rate_limit_register_per_minute: int = Field(default=10, alias="RATE_LIMIT_REGISTER_PER_MINUTE")

    catalog_default_limit: int = Field(default=50, alias="CATALOG_DEFAULT_LIMIT")
    catalog_max_limit: int = Field(default=100, alias="CATALOG_MAX_LIMIT")
    catalog_search_max_length: int = Field(default=200, alias="CATALOG_SEARCH_MAX_LENGTH")

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def resolve_database_url() -> str:
    """Database URL from Settings (.env + environment, Pydantic precedence)."""
    return get_settings().database_url


def resolve_test_database_url() -> str:
    """Integration test database URL from Settings (.env + environment)."""
    return get_settings().test_database_url.strip()


def database_name_from_url(url: str) -> str:
    parsed = urlparse(url.replace("+pymysql", ""))
    return (parsed.path or "").lstrip("/").split("?")[0]


def alembic_ini_sqlalchemy_url(database_url: str) -> str:
    """Escape ``%`` for Alembic ConfigParser when setting ``sqlalchemy.url``."""
    return database_url.replace("%", "%%")


def migration_url_from_alembic_config(config: object) -> str:
    """URL for Alembic runs: honor ``Config.set_main_option`` unless ini still has the placeholder."""
    get_main_option = config.get_main_option  # type: ignore[attr-defined]
    configured = (get_main_option("sqlalchemy.url") or "").strip()
    if configured and configured != ALEMBIC_INI_DEFAULT_URL:
        return configured
    return resolve_database_url()


def redact_database_url(url: str) -> str:
    """Return a URL safe for logs and user-facing errors (password hidden)."""
    try:
        parsed = make_url(url)
    except Exception:
        return "<invalid-database-url>"
    return parsed.render_as_string(hide_password=True)


def integration_database_url_error(url: str) -> str | None:
    """Validate TEST_DATABASE_URL for integration verification; message never contains secrets."""
    if not url.strip():
        return "TEST_DATABASE_URL is not set"
    db_name = database_name_from_url(url)
    if db_name == "jpetstore":
        return "Integration verification must not target database jpetstore"
    if db_name != "jpetstore_test":
        return "TEST_DATABASE_URL must target database jpetstore_test"
    config_error = database_url_configuration_error(url)
    if config_error:
        return config_error.replace("DATABASE_URL", "TEST_DATABASE_URL")
    return None


def database_url_configuration_error(url: str) -> str | None:
    """Return a user-facing message when DATABASE_URL is not ready for MySQL, else None."""
    if "<password>" in url:
        return (
            "DATABASE_URL still contains the literal <password> placeholder. "
            "Edit .env: set the same password you used when creating MySQL user jpetstore_app "
            "(see scripts/mysql-local-setup.sql). URL-encode special characters in the password."
        )
    try:
        parsed = make_url(url)
    except Exception:
        return "DATABASE_URL is not a valid SQLAlchemy URL."
    if not parsed.drivername.startswith("mysql"):
        return None
    if not parsed.password:
        return "DATABASE_URL is missing a password for the MySQL user."
    return None
