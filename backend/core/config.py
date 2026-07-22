from enum import Enum
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class AppSettings(BaseSettings):
    title: str = "Sentinel API"
    description: str = "Industrial Safety Operating System Backend"
    version: str = "1.0.0"
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    api_v1_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")





class RedisSettings(BaseSettings):
    url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_prefix="REDIS_", env_file=".env", extra="ignore")


class KafkaSettings(BaseSettings):
    broker: str = "localhost:9092"

    model_config = SettingsConfigDict(env_prefix="KAFKA_", env_file=".env", extra="ignore")





class ChromaSettings(BaseSettings):
    host: str = "api.trychroma.com"
    api_key: str = ""
    tenant: str = ""
    database: str = "default"

    model_config = SettingsConfigDict(env_prefix="CHROMA_", env_file=".env", extra="ignore")


class GeminiSettings(BaseSettings):
    api_key: str = "gemini-placeholder"

    model_config = SettingsConfigDict(env_prefix="GEMINI_", env_file=".env", extra="ignore")


class MapboxSettings(BaseSettings):
    token: str = "pk.placeholder"

    model_config = SettingsConfigDict(env_prefix="MAPBOX_", env_file=".env", extra="ignore")


class SecuritySettings(BaseSettings):
    jwt_secret: str = "super-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    allowed_hosts: list[str] = ["*"]
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(env_prefix="SECURITY_", env_file=".env", extra="ignore")


class LoggingSettings(BaseSettings):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Literal["json", "console"] = "json"

    model_config = SettingsConfigDict(env_prefix="LOGGING_", env_file=".env", extra="ignore")


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    redis: RedisSettings = RedisSettings()
    kafka: KafkaSettings = KafkaSettings()
    chroma: ChromaSettings = ChromaSettings()
    gemini: GeminiSettings = GeminiSettings()
    mapbox: MapboxSettings = MapboxSettings()
    security: SecuritySettings = SecuritySettings()
    logging: LoggingSettings = LoggingSettings()

settings = Settings()
