# /api/messages.py

from __future__ import annotations

import httpx
from fastapi import APIRouter, Response

from config.settings import settings
from core.log.log import (
    logger,
    START_MODULE_MESSAGE,
    str_object_is_created,
)


MODULE_DESCRIPTION = "This module defines API endpoints for sending messages and simulating errors"


router = APIRouter()


@router.post("/api/message-a", status_code=200)
async def message_a() -> Response:
    async with httpx.AsyncClient(base_url=settings.SERVICE_B_URL) as client:
        response = await client.post("/api/message-b")
        response.raise_for_status()
    return Response(status_code=200)


@router.post("/api/error")
async def error(code: int = 500) -> Response:
    return Response(status_code=code)


def main() -> None:
    logger.info(START_MODULE_MESSAGE + str(__file__))
    logger.info(MODULE_DESCRIPTION)
    logger.info(str_object_is_created(router))


if __name__ != "__main__":
    main()


if __name__ == "__main__":
    main()
