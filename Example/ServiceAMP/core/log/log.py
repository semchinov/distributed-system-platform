# /core/log/log.py

from __future__ import annotations

import logging
import sys
from loguru import logger
from typing import Any



MODULE_DESCRIPTION = "This module stores logger settings and configurations"


START_MODULE_MESSAGE = "You have launched the module "


class InterceptHandler(logging.Handler):
    """
    This class intercepts logging messages and
    redirects them from logging logger (standard
    python) to loguru logger.
    """
    def emit(self, record: logging.LogRecord) -> None:
        # logging levels are INFO DEBUG and so on
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    """
    This function sets up the logging configuration for the application.
    """

    # delete default sink by loguru
    logger.remove()

    logger.add(
        sys.stdout,
        enqueue=True,
        backtrace=True,
        diagnose=False,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "{name}:{file}:{function}:{line} | <level>{message}</level>",
    )

    # send ALL to InterceptHandler
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # uvicorn creates its own loggers - we have to intercept them
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()


# Function for dynamic logger information (Python module info)
def str_object_is_created(created_object: Any) -> str:
    """
        Function for making string with description of creation of object
            Parameters:
                created_object: creation of this object we should describe
            Returns:
                str: description of creation of object
    """
    return f"Object {created_object} is created"


setup_logging()


def main() -> None:
    logger.info("Logging has been set up successfully.")
    logger.info(START_MODULE_MESSAGE + str(__file__))
    logger.info(MODULE_DESCRIPTION)
    logger.info(str_object_is_created(logger))


if __name__ != "__main__":
    main()


if __name__ == "__main__":
    main()
