# /__main__.py

import uvicorn

from config.settings import settings
from core.log.log import logger, START_MODULE_MESSAGE, str_object_is_created



MODULE_DESCRIPTION = "This module starts the Service A ASGI server"


def main() -> None:
    logger.info(START_MODULE_MESSAGE + str(__file__))
    logger.info(MODULE_DESCRIPTION)
    uvicorn.run(
        "api.app:app",
        host=settings.HOST,
        port=settings.BACKEND_PORT,
        log_config=None,
        proxy_headers=True,
    )


if __name__ != "__main__":
    main()


if __name__ == "__main__":
    main()
