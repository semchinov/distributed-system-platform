# /config/settings.py

from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.log.log import (
    logger,
    START_MODULE_MESSAGE,
    str_object_is_created
)


MODULE_DESCRIPTION = "This module is used to save all creds and settings for the program"


_THIS_FILE  = Path(__file__).resolve()
ROOT_DIR    = _THIS_FILE.parents[1]            # /config/settings.py -> config -> root
DEFAULT_ENV = ROOT_DIR / ".env"                # root/.env
ENV_FILE    = str(DEFAULT_ENV) if DEFAULT_ENV.exists() else ".env"

if not DEFAULT_ENV.exists():
    logger.warning(f".env file not found at: {DEFAULT_ENV}")

class Config(BaseSettings):

    # region backendSettings

    BACKEND_PORT: int | None = None

    # endregion backendSettings

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Config()


def main():
    logger.info(START_MODULE_MESSAGE)
    logger.info(MODULE_DESCRIPTION)
    logger.info(str_object_is_created(settings))


if __name__ != "__main__":
    main()


if __name__ == "__main__":
    main()
