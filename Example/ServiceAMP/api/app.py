# /api/app.py

from __future__ import annotations

from fastapi import FastAPI

from app.api.routers.job import router as job_router
from app.api.routers.messages import router as messages_router
from app.config.settings import settings
from app.core.log.log import (
    logger,
    START_MODULE_MESSAGE,
    str_object_is_created,
)
from app.core.observability import instrument_app, setup_telemetry


MODULE_DESCRIPTION = "This module builds the FastAPI application"


def create_app() -> FastAPI:
    setup_telemetry(
        endpoint=settings.OPENTELEMETRY_ENDPOINT,
        service_name=settings.SERVICE_NAME,
    )
    app = FastAPI()
    instrument_app(app)
    app.include_router(messages_router)
    app.include_router(job_router)
    return app


def main() -> None:
    logger.info(START_MODULE_MESSAGE)
    logger.info(MODULE_DESCRIPTION)
    logger.info(str_object_is_created(create_app()))


if __name__ != "__main__":
    main()


if __name__ == "__main__":
    main()
