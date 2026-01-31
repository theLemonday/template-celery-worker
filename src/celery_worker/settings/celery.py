from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from celery_worker.settings.redis import RedisSettings


class AppSettings(BaseSettings):
    name: str = "celery-worker"
    # We reuse the same RedisConfig class for two different purposes
    celery_broker: RedisSettings = Field(default_factory=lambda: RedisSettings(db=0))
    celery_backend: RedisSettings = Field(default_factory=lambda: RedisSettings(db=1))

    # This allows you to use double underscores in env vars to target nested fields
    # Example: CELERY_BROKER__HOST=10.0.0.1
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_prefix="APP_")

    @property
    def broker_url(self) -> str:
        return self.celery_broker.dsn

    @property
    def result_backend(self) -> str:
        return self.celery_backend.dsn


# Instantiate settings
settings = AppSettings()
