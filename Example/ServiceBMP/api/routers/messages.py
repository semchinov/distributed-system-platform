# /api/routers/messages.py

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import TypedDict
from fastapi import APIRouter, Header, Response
from fastapi.responses import JSONResponse

from config.settings import settings
from core.log.log import logger, START_MODULE_MESSAGE, str_object_is_created
from core.observability import get_delivery_messages_received_counter


MODULE_DESCRIPTION = "This module defines HTTP endpoints for Service B messages"


class ProcessedMessageResult(TypedDict):
    """Result of processing a message (stored for idempotency)"""
    message_id: str
    processed_at: str
    status: str
    processing_count: int


# Global storage for processed messages and lock for concurrency safety
processed_messages: dict[str, ProcessedMessageResult] = {}
processed_messages_lock: asyncio.Lock | None = None


async def _get_lock() -> asyncio.Lock:
    """Lazy initialization of asyncio.Lock to avoid event loop issues at import time."""
    global processed_messages_lock
    if processed_messages_lock is None:
        processed_messages_lock = asyncio.Lock()
    return processed_messages_lock


router = APIRouter()


async def _process_message(message_id: str) -> ProcessedMessageResult:
    """
    Simulated business logic for processing a message.
    In a real system, this would be actual business logic.
    """
    logger.info(f"Executing business logic for message_id={message_id}")
    result: ProcessedMessageResult = {
        "message_id": message_id,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "status": "processed",
        "processing_count": 1,
    }
    return result


@router.post("/api/message-b", status_code=200)
async def message_b(x_message_id: str | None = Header(None)) -> Response:
    """
    Receive a message with optional idempotency via X-Message-Id header.
    Implements exactly-once processing semantics.
    """
    # Check for required X-Message-Id header
    if not x_message_id:
        logger.warning("Received request without X-Message-Id header")
        return Response(status_code=400, content="Missing X-Message-Id header")

    logger.info(f"Received message with message_id={x_message_id}")

    # Increment received counter immediately (for all valid requests)
    try:
        counter = get_delivery_messages_received_counter()
        counter.add(1, {"service_name": settings.SERVICE_NAME, "message_id": x_message_id})
        logger.info(f"Incremented delivery_messages_received_total for message_id={x_message_id}")
    except Exception as exc:
        logger.warning(f"Failed to increment delivery_messages_received_total: {exc}")

    # Check for idempotency using lock to avoid race conditions
    lock = await _get_lock()
    async with lock:
        if x_message_id in processed_messages:
            # Message already processed - return cached result
            cached_result = processed_messages[x_message_id]
            logger.info(f"Message_id={x_message_id} already processed at {cached_result['processed_at']}; returning cached result")
            cached_result["processing_count"] = cached_result.get("processing_count", 1) + 1
            return JSONResponse(status_code=200, content=cached_result)

        # First time seeing this message_id - process it
        result = await _process_message(x_message_id)
        processed_messages[x_message_id] = result
        logger.info(f"Message_id={x_message_id} processed for the first time")
        return JSONResponse(status_code=200, content=result)


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
