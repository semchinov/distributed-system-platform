# /api/routers/messages.py

from __future__ import annotations

import asyncio
import uuid

import httpx
from fastapi import APIRouter, Response

from config.settings import settings
from core.log.log import logger, START_MODULE_MESSAGE, str_object_is_created
from core.observability import get_delivery_messages_sent_counter


MODULE_DESCRIPTION = "This module defines HTTP endpoints for Service A messages"


router = APIRouter()


async def _send_with_retry(message_id: str) -> None:
    max_attempts = settings.DELIVERY_MAX_ATTEMPTS
    timeout_seconds = settings.DELIVERY_REQUEST_TIMEOUT_SECONDS
    backoff_base = settings.DELIVERY_RETRY_BACKOFF_SECONDS

    async with httpx.AsyncClient(base_url=settings.SERVICE_B_URL, timeout=timeout_seconds) as client:
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Attempt {attempt} sending message_id={message_id} to {settings.SERVICE_B_URL}")
                response = await client.post(
                    "/api/message-b",
                    headers={"X-Message-Id": message_id},
                )
                # If response is 4xx do not retry
                if 400 <= response.status_code < 500:
                    logger.error(f"Received non-retriable status {response.status_code} for message_id={message_id}")
                    response.raise_for_status()
                # For 5xx raise for retry handling
                if 500 <= response.status_code < 600:
                    logger.warning(f"Received retriable server error {response.status_code} for message_id={message_id}")
                    # let exception flow to retry handling
                    response.raise_for_status()

                logger.info(f"Successfully sent message_id={message_id}")
                return

            except httpx.HTTPStatusError as exc:
                # status errors are raised by raise_for_status()
                logger.warning(f"HTTPStatusError on attempt {attempt} for message_id={message_id}: {exc}")
                if attempt >= max_attempts:
                    logger.error(f"Exhausted attempts for message_id={message_id}")
                    raise
            except (httpx.RequestError, httpx.TimeoutException) as exc:  # network/timeout
                logger.warning(f"Request error on attempt {attempt} for message_id={message_id}: {exc}")
                if attempt >= max_attempts:
                    logger.error(f"Exhausted attempts for message_id={message_id}")
                    raise
            # backoff before next attempt
            await asyncio.sleep(backoff_base * attempt)


@router.post("/api/message-a", status_code=200)
async def message_a() -> Response:
    # Generate message_id immediately
    message_id = str(uuid.uuid4())
    logger.info(f"Incoming request received; generated message_id={message_id}")

    # Increment delivery_messages_sent_total immediately
    try:
        counter = get_delivery_messages_sent_counter()
        counter.add(1, {"message_id": message_id})
        logger.info(f"Incremented delivery_messages_sent_total for message_id={message_id}")
    except Exception as exc:
        logger.warning(f"Failed to increment delivery_messages_sent_total: {exc}")

    scenario = (settings.DELIVERY_SCENARIO or "no_checks").lower()
    logger.info(f"Delivery scenario: {scenario}")

    # Perform send according to scenario
    if scenario == "no_checks":
        # send once; do not retry
        try:
            async with httpx.AsyncClient(base_url=settings.SERVICE_B_URL, timeout=settings.DELIVERY_REQUEST_TIMEOUT_SECONDS) as client:
                logger.info(f"Sending message_id={message_id} to ServiceB (no_checks)")
                response = await client.post("/api/message-b", headers={"X-Message-Id": message_id})
                response.raise_for_status()
                logger.info(f"Sent message_id={message_id} successfully (no_checks)")
        except Exception as exc:
            logger.error(f"Error sending message_id={message_id} (no_checks): {exc}")
            # At-most-once: do not retry, return 502
            return Response(status_code=502)

    elif scenario in ("retry", "retry_idempotent"):
        # Do retries with same message_id
        try:
            await _send_with_retry(message_id)
        except Exception as exc:
            logger.error(f"Final failure sending message_id={message_id}: {exc}")
            return Response(status_code=502)

    else:
        logger.warning(f"Unknown DELIVERY_SCENARIO={scenario}; defaulting to no_checks behavior")
        try:
            async with httpx.AsyncClient(base_url=settings.SERVICE_B_URL, timeout=settings.DELIVERY_REQUEST_TIMEOUT_SECONDS) as client:
                response = await client.post("/api/message-b", headers={"X-Message-Id": message_id})
                response.raise_for_status()
        except Exception as exc:
            logger.error(f"Error sending message_id={message_id}: {exc}")
            return Response(status_code=502)

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
