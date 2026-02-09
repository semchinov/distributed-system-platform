import uvicorn

from ServiceAMP.config.settings import settings
from ServiceAMP.core.log.log import logger


def main() -> None:
    logger.info("Starting Service A (Python)")
    uvicorn.run(
        "ServiceAMP.api.app:app",
        host=settings.HOST,
        port=settings.BACKEND_PORT,
        log_config=None,
        proxy_headers=True,
    )


if __name__ == "__main__":
    main()
