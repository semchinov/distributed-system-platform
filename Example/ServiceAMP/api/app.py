# /api/app.py

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from ServiceAMP.api.routers.messages import router as messages_router
from ServiceAMP.config.settings import settings
from ServiceAMP.core.log.log import (
    logger,
    START_MODULE_MESSAGE,
    str_object_is_created,
)
from ServiceAMP.core.observability import instrument_app, setup_telemetry


MODULE_DESCRIPTION = "This module builds the FastAPI application"


def create_app() -> FastAPI:
    setup_telemetry(
        endpoint=settings.OPENTELEMETRY_ENDPOINT,
        service_name=settings.SERVICE_NAME,
    )
    app = FastAPI(docs_url="/swagger", openapi_url="/swagger/v1/swagger.json")
    instrument_app(app)
    app.include_router(messages_router)

    @app.get("/swagger/index.html", include_in_schema=False)
    async def swagger_index() -> RedirectResponse:
        return RedirectResponse(url="/swagger")

    return app


app = create_app()


def main() -> None:
    logger.info(START_MODULE_MESSAGE)
    logger.info(MODULE_DESCRIPTION)
    logger.info(str_object_is_created(create_app()))


if __name__ != "__main__":
    main()


if __name__ == "__main__":
    main()
