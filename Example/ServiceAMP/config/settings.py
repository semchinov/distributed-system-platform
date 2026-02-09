# /config/settings.py

from __future__ import annotations

from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.log.log import logger, START_MODULE_MESSAGE, str_object_is_created



MODULE_DESCRIPTION = "This module stores configuration and environment settings"


_THIS_FILE = Path(__file__).resolve()
ROOT_DIR = _THIS_FILE.parents[1]  # /config/settings.py -> config -> root
DEFAULT_ENV = ROOT_DIR / ".env"  # root/.env
ENV_FILE = str(DEFAULT_ENV) if DEFAULT_ENV.exists() else ".env"

if not DEFAULT_ENV.exists():
    logger.warning(f".env file not found at: {DEFAULT_ENV}")

class Config(BaseSettings):
    SERVICE_NAME: str = Field(default="service-a")
    SERVICE_B_URL: str = Field(
        default="http://service-b",
        validation_alias=AliasChoices(
            "SERVICE_B_URL",
            "SERVICE_B__URL",
            "ServiceB__Url",
            "ServiceB__URL",
        ),
    )
    OPENTELEMETRY_ENDPOINT: str = Field(
        default="http://otel-collector:4317",
        validation_alias=AliasChoices(
            "OPENTELEMETRY_ENDPOINT",
            "OPENTELEMETRY__ENDPOINT",
            "OpenTelemetry__Endpoint",
        ),
    )
    HOST: str = Field(default="0.0.0.0")
    BACKEND_PORT: int = Field(default=80, validation_alias=AliasChoices("PORT", "BACKEND_PORT"))

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Config()


def main() -> None:
    logger.info(START_MODULE_MESSAGE + str(__file__))
    logger.info(MODULE_DESCRIPTION)
    logger.info(str_object_is_created(settings))


if __name__ != "__main__":
    main()


if __name__ == "__main__":
    main()
