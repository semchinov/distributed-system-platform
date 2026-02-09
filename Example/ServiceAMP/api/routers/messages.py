from __future__ import annotations

import httpx
from fastapi import APIRouter, Response

from ServiceAMP.config.settings import settings

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
