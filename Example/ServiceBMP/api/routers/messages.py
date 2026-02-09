# /api/routers/messages.py

from __future__ import annotations

from fastapi import APIRouter, Response

from core.log.log import logger, START_MODULE_MESSAGE, str_object_is_created



MODULE_DESCRIPTION = "This module defines HTTP endpoints for Service B messages"


router = APIRouter()


@router.post("/api/message-b", status_code=200)
async def message_b() -> Response:
    return Response(status_code=200)


def main() -> None:
    logger.info(START_MODULE_MESSAGE + str(__file__))
    logger.info(MODULE_DESCRIPTION)
    logger.info(str_object_is_created(router))


if __name__ != "__main__":
    main()


if __name__ == "__main__":
    main()
